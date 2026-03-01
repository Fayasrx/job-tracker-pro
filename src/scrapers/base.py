"""
Base scraper with shared HTTP session logic and anti-detection.
"""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from fake_useragent import UserAgent

from ..models import JobListing, SearchQuery
from ..utils.logger import log


class BaseScraper(ABC):
    """Abstract base class for all job platform scrapers."""

    PLATFORM: str = ""
    BASE_URL: str = ""
    RATE_LIMIT_DELAY: tuple[float, float] = (1.5, 4.0)  # random delay range

    def __init__(self):
        self._ua = UserAgent()
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def headers(self) -> dict:
        return {
            "User-Agent": self._ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True,
                limits=httpx.Limits(max_connections=5),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _rate_limit(self):
        delay = random.uniform(*self.RATE_LIMIT_DELAY)
        await asyncio.sleep(delay)

    async def fetch(self, url: str, params: dict = None) -> Optional[str]:
        """Fetch a URL with rate limiting and error handling."""
        try:
            await self._rate_limit()
            client = await self.get_client()
            resp = await client.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPStatusError as e:
            log.warning(f"[{self.PLATFORM}] HTTP {e.response.status_code} for {url}")
            return None
        except Exception as e:
            log.error(f"[{self.PLATFORM}] Fetch error: {e}")
            return None

    async def fetch_json(self, url: str, params: dict = None) -> Optional[dict]:
        """Fetch JSON endpoint."""
        try:
            await self._rate_limit()
            client = await self.get_client()
            resp = await client.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.error(f"[{self.PLATFORM}] JSON fetch error: {e}")
            return None

    @abstractmethod
    async def search(self, query: SearchQuery) -> list[JobListing]:
        """Search for jobs. Must be implemented by each platform scraper."""
        ...

    @abstractmethod
    async def get_job_details(self, job_id: str) -> Optional[JobListing]:
        """Get full details for a specific job."""
        ...
