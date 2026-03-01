"""
LinkedIn Jobs scraper using public job search endpoints.
Uses LinkedIn's public job search (no login required for searching).
"""

import hashlib
import re
from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import JobListing, SearchQuery
from ..utils.logger import log


class LinkedInScraper(BaseScraper):
    PLATFORM = "linkedin"
    BASE_URL = "https://www.linkedin.com"

    # Date filter mapping
    DATE_MAP = {
        "24h": "r86400",
        "3d": "r259200",
        "7d": "r604800",
        "14d": "r1209600",
        "30d": "r2592000",
    }

    # Experience level mapping
    EXP_MAP = {
        "fresher": "1",      # Entry level
        "entry": "1",
        "associate": "2",
        "mid": "3",
        "senior": "4",
        "director": "5",
        "executive": "6",
    }

    async def search(self, query: SearchQuery) -> list[JobListing]:
        """Search LinkedIn public job listings."""
        all_jobs: list[JobListing] = []

        for role in query.roles:
            for location in query.locations:
                jobs = await self._search_role_location(
                    role, location, query
                )
                all_jobs.extend(jobs)

                if len(all_jobs) >= query.max_results_per_platform:
                    return all_jobs[:query.max_results_per_platform]

        return all_jobs[:query.max_results_per_platform]

    async def _search_role_location(
        self, role: str, location: str, query: SearchQuery
    ) -> list[JobListing]:
        """Search for a specific role in a specific location."""
        params = {
            "keywords": role,
            "location": location,
            "f_TPR": self.DATE_MAP.get(query.posted_within, "r604800"),
            "f_E": self.EXP_MAP.get(query.experience, "1"),
            "position": "1",
            "pageNum": "0",
            "start": "0",
        }

        url = f"{self.BASE_URL}/jobs-guest/jobs/api/seeMoreJobPostings/search"
        html = await self.fetch(url, params=params)

        if not html:
            # Fallback to regular search page
            search_url = f"{self.BASE_URL}/jobs/search"
            html = await self.fetch(search_url, params=params)

        if not html:
            log.warning(f"[LinkedIn] No results for {role} in {location}")
            return []

        return self._parse_search_results(html, role, location)

    def _parse_search_results(self, html: str, role: str, location: str) -> list[JobListing]:
        """Parse LinkedIn job search results HTML."""
        jobs = []
        soup = BeautifulSoup(html, "lxml")

        # LinkedIn job cards
        cards = soup.find_all("li") or soup.find_all("div", class_=re.compile(r"job-search-card"))

        for card in cards:
            try:
                # Title
                title_el = card.find("h3") or card.find(class_=re.compile(r"base-search-card__title"))
                title = title_el.get_text(strip=True) if title_el else ""

                if not title:
                    continue

                # Company
                company_el = card.find("h4") or card.find(class_=re.compile(r"base-search-card__subtitle"))
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                # Location
                loc_el = card.find(class_=re.compile(r"job-search-card__location"))
                loc = loc_el.get_text(strip=True) if loc_el else location

                # Find specific LinkedIn Job ID from the card
                real_job_id = ""
                urn_el = card.find(attrs={"data-job-id": True}) or card.find(attrs={"data-entity-urn": True})
                if urn_el:
                    if urn_el.get("data-job-id"):
                        real_job_id = urn_el.get("data-job-id")
                    elif urn_el.get("data-entity-urn"):
                        # format is typically urn:li:jobPosting:1234567890
                        parts = urn_el.get("data-entity-urn").split(":")
                        if len(parts) > 0:
                            real_job_id = parts[-1]

                # URL
                link = card.find("a", href=re.compile(r"/jobs/view/|/jobPostings/|/jobs/search")) or card.find("a", href=True)
                url = link["href"] if link and link.get("href") else ""
                
                if real_job_id:
                    url = f"{self.BASE_URL}/jobs/view/{real_job_id}/"
                elif url:
                    if not url.startswith("http"):
                        url = f"{self.BASE_URL}{url if url.startswith('/') else '/' + url}"
                    # Try to parse currentJobId if stuck in a search redirect
                    match = re.search(r"currentJobId=(\d+)", url)
                    if match:
                        url = f"{self.BASE_URL}/jobs/view/{match.group(1)}/"
                else:
                    url = f"{self.BASE_URL}/jobs/search/?keywords={quote_plus(title)}+{quote_plus(company)}&location={quote_plus(loc)}"

                # Posted date
                date_el = card.find("time") or card.find(class_=re.compile(r"job-search-card__listdate"))
                posted = date_el.get_text(strip=True) if date_el else ""

                job_id = hashlib.md5(f"linkedin_{title}_{company}".encode()).hexdigest()[:12]

                jobs.append(JobListing(
                    id=f"li_{job_id}",
                    title=title,
                    company=company,
                    location=loc,
                    url=url,
                    platform="linkedin",
                    posted_date=posted,
                    experience=role,
                ))
            except Exception as e:
                log.debug(f"[LinkedIn] Parse error on card: {e}")
                continue

        log.info(f"[LinkedIn] Found {len(jobs)} jobs for '{role}' in '{location}'")
        return jobs

    async def get_job_details(self, job_id: str) -> Optional[JobListing]:
        """Get detailed job description from LinkedIn."""
        return None  # LinkedIn requires auth for full details
