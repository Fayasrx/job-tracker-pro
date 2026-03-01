"""
Indeed Jobs scraper using public search pages.
"""

import hashlib
import re
from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import JobListing, SearchQuery
from ..utils.logger import log


class IndeedScraper(BaseScraper):
    PLATFORM = "indeed"
    BASE_URL = "https://in.indeed.com"  # India Indeed

    DATE_MAP = {
        "24h": "1",
        "3d": "3",
        "7d": "7",
        "14d": "14",
        "30d": "",
    }

    async def search(self, query: SearchQuery) -> list[JobListing]:
        """Search Indeed for jobs."""
        all_jobs: list[JobListing] = []

        for role in query.roles:
            for location in query.locations:
                jobs = await self._search_role(role, location, query)
                all_jobs.extend(jobs)
                if len(all_jobs) >= query.max_results_per_platform:
                    return all_jobs[:query.max_results_per_platform]

        return all_jobs[:query.max_results_per_platform]

    async def _search_role(self, role: str, location: str, query: SearchQuery) -> list[JobListing]:
        params = {
            "q": role,
            "l": location,
            "fromage": self.DATE_MAP.get(query.posted_within, "7"),
            "sort": "date",
        }

        if query.experience == "fresher":
            params["explvl"] = "entry_level"

        html = await self.fetch(f"{self.BASE_URL}/jobs", params=params)
        if not html:
            return []

        return self._parse(html, role, location)

    def _parse(self, html: str, role: str, location: str) -> list[JobListing]:
        jobs = []
        soup = BeautifulSoup(html, "lxml")

        cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|cardOutline|resultContent"))

        for card in cards:
            try:
                title_el = card.find("h2") or card.find(class_=re.compile(r"jobTitle"))
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                company_el = card.find(attrs={"data-testid": "company-name"}) or card.find(class_=re.compile(r"company"))
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                loc_el = card.find(attrs={"data-testid": "text-location"}) or card.find(class_=re.compile(r"companyLocation"))
                loc = loc_el.get_text(strip=True) if loc_el else location

                salary_el = card.find(class_=re.compile(r"salary|estimated-salary"))
                salary = salary_el.get_text(strip=True) if salary_el else ""

                link = card.find("a", href=re.compile(r"/rc/clk|/viewjob"))
                url = ""
                if link:
                    href = link.get("href", "")
                    if href.startswith("http"):
                        url = href
                    else:
                        url = f"{self.BASE_URL}{href if href.startswith('/') else '/' + href}"
                if not url:
                    url = f"{self.BASE_URL}/jobs?q={quote_plus(title)}+{quote_plus(company)}&l={quote_plus(loc)}"

                job_id = hashlib.md5(f"indeed_{title}_{company}".encode()).hexdigest()[:12]

                jobs.append(JobListing(
                    id=f"in_{job_id}",
                    title=title,
                    company=company,
                    location=loc,
                    salary=salary,
                    url=url,
                    platform="indeed",
                    experience=role,
                ))
            except Exception as e:
                log.debug(f"[Indeed] Parse error: {e}")
                continue

        log.info(f"[Indeed] Found {len(jobs)} jobs for '{role}' in '{location}'")
        return jobs

    async def get_job_details(self, job_id: str) -> Optional[JobListing]:
        return None
