"""
Internshala Jobs & Internships scraper.
"""

import hashlib
import re
from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import JobListing, SearchQuery
from ..utils.logger import log


class InternshalaScraper(BaseScraper):
    PLATFORM = "internshala"
    BASE_URL = "https://internshala.com"

    async def search(self, query: SearchQuery) -> list[JobListing]:
        all_jobs: list[JobListing] = []

        for role in query.roles:
            # Search both internships and fresher jobs
            jobs_intern = await self._search_internships(role, query)
            jobs_fresher = await self._search_fresher_jobs(role, query)
            all_jobs.extend(jobs_intern)
            all_jobs.extend(jobs_fresher)

            if len(all_jobs) >= query.max_results_per_platform:
                return all_jobs[:query.max_results_per_platform]

        return all_jobs[:query.max_results_per_platform]

    async def _search_internships(self, role: str, query: SearchQuery) -> list[JobListing]:
        role_slug = role.lower().replace(" ", "-").replace("/", "-")

        locations = ",".join(l.lower() for l in query.locations if l.lower() != "remote")
        loc_part = f"/in-{locations.replace(',', ',in-')}" if locations else ""

        url = f"{self.BASE_URL}/internships/{role_slug}-internship{loc_part}"

        html = await self.fetch(url)
        if not html:
            return []

        return self._parse(html, "internship")

    async def _search_fresher_jobs(self, role: str, query: SearchQuery) -> list[JobListing]:
        role_slug = role.lower().replace(" ", "-").replace("/", "-")
        url = f"{self.BASE_URL}/fresher-jobs/{role_slug}-jobs"

        html = await self.fetch(url)
        if not html:
            return []

        return self._parse(html, "fresher-job")

    def _parse(self, html: str, listing_type: str) -> list[JobListing]:
        jobs = []
        soup = BeautifulSoup(html, "lxml")

        cards = soup.find_all("div", class_=re.compile(r"individual_internship|internship_meta"))
        if not cards:
            cards = soup.find_all("div", id=re.compile(r"internship_"))

        for card in cards:
            try:
                title_el = card.find("h3") or card.find(class_=re.compile(r"profile|heading"))
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                company_el = card.find(class_=re.compile(r"company_name|company")) or card.find("h4")
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                loc_el = card.find(class_=re.compile(r"location"))
                loc = loc_el.get_text(strip=True) if loc_el else ""

                stipend_el = card.find(class_=re.compile(r"stipend|salary"))
                stipend = stipend_el.get_text(strip=True) if stipend_el else ""

                link = card.find("a", class_=re.compile(r"view_detail_button")) or card.find("a", href=re.compile(r"/job/|/internship/")) or card.find("a", href=True)
                url = ""
                
                if link:
                    href = link.get("href", "")
                    if href.startswith("http"):
                        url = href
                    elif href:
                        url = f"{self.BASE_URL}{href if href.startswith('/') else '/' + href}"
                
                if not url or url == f"{self.BASE_URL}/" or url.endswith("/jobs/"):
                    role_slug = quote_plus(title.lower().replace(" ", "-") or "internship")
                    url = f"{self.BASE_URL}/internships/{role_slug}-internship"

                job_type = "Internship" if listing_type == "internship" else "Full-time"

                job_id = hashlib.md5(f"internshala_{title}_{company}".encode()).hexdigest()[:12]

                jobs.append(JobListing(
                    id=f"is_{job_id}",
                    title=title,
                    company=company,
                    location=loc,
                    salary=stipend,
                    url=url,
                    platform="internshala",
                    job_type=job_type,
                ))
            except Exception as e:
                log.debug(f"[Internshala] Parse error: {e}")
                continue

        log.info(f"[Internshala] Found {len(jobs)} {listing_type}s")
        return jobs

    async def get_job_details(self, job_id: str) -> Optional[JobListing]:
        return None
