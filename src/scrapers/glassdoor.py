"""
Glassdoor Jobs scraper using public search.
"""

import hashlib
import re
from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import JobListing, SearchQuery
from ..utils.logger import log


class GlassdoorScraper(BaseScraper):
    PLATFORM = "glassdoor"
    BASE_URL = "https://www.glassdoor.co.in"

    async def search(self, query: SearchQuery) -> list[JobListing]:
        all_jobs: list[JobListing] = []

        for role in query.roles:
            for location in query.locations:
                jobs = await self._search_role(role, location, query)
                all_jobs.extend(jobs)
                if len(all_jobs) >= query.max_results_per_platform:
                    return all_jobs[:query.max_results_per_platform]

        return all_jobs[:query.max_results_per_platform]

    async def _search_role(self, role: str, location: str, query: SearchQuery) -> list[JobListing]:
        keyword = quote_plus(role)
        loc = quote_plus(location)

        # Glassdoor search URL format
        url = f"{self.BASE_URL}/Job/jobs.htm"
        params = {
            "sc.keyword": role,
            "locT": "C",
            "locKeyword": location,
            "jobType": "",
            "fromAge": "7" if query.posted_within == "7d" else "3",
            "seniorityType": "entrylevel" if query.experience == "fresher" else "",
        }

        html = await self.fetch(url, params=params)
        if not html:
            return []

        return self._parse(html, role, location)

    def _parse(self, html: str, role: str, location: str) -> list[JobListing]:
        jobs = []
        soup = BeautifulSoup(html, "lxml")

        cards = soup.find_all("li", class_=re.compile(r"JobsList_jobListItem|react-job-listing"))

        for card in cards:
            try:
                title_el = card.find("a", class_=re.compile(r"jobTitle|JobCard_jobTitle"))
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                company_el = card.find(class_=re.compile(r"EmployerProfile_compactEmployerName|employer"))
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                loc_el = card.find(class_=re.compile(r"location|JobCard_location"))
                loc = loc_el.get_text(strip=True) if loc_el else location

                salary_el = card.find(class_=re.compile(r"salary"))
                salary = salary_el.get_text(strip=True) if salary_el else ""

                link = card.find("a", href=True)
                url = ""
                if link:
                    href = link.get("href", "")
                    if href.startswith("http"):
                        url = href
                    elif href:
                        url = f"{self.BASE_URL}{href if href.startswith('/') else '/' + href}"
                if not url:
                    url = f"{self.BASE_URL}/Job/jobs.htm?sc.keyword={quote_plus(title)}+{quote_plus(company)}&locKeyword={quote_plus(loc)}"

                job_id = hashlib.md5(f"glassdoor_{title}_{company}".encode()).hexdigest()[:12]

                jobs.append(JobListing(
                    id=f"gd_{job_id}",
                    title=title,
                    company=company,
                    location=loc,
                    salary=salary,
                    url=url,
                    platform="glassdoor",
                    experience=role,
                ))
            except Exception as e:
                log.debug(f"[Glassdoor] Parse error: {e}")
                continue

        log.info(f"[Glassdoor] Found {len(jobs)} jobs for '{role}' in '{location}'")
        return jobs

    async def get_job_details(self, job_id: str) -> Optional[JobListing]:
        return None
