"""
Naukri.com Jobs scraper using public search API.
"""

import hashlib
import re
from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import JobListing, SearchQuery
from ..utils.logger import log


class NaukriScraper(BaseScraper):
    PLATFORM = "naukri"
    BASE_URL = "https://www.naukri.com"

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
        # Naukri URL format: /role-jobs-in-location
        role_slug = role.lower().replace(" ", "-").replace("/", "-")
        loc_slug = location.lower().replace(" ", "-")

        experience = "0" if query.experience == "fresher" else "1"

        url = f"{self.BASE_URL}/{role_slug}-jobs-in-{loc_slug}"
        params = {
            "experience": experience,
        }

        html = await self.fetch(url, params=params)
        if not html:
            # Fallback: direct search
            params = {
                "k": role,
                "l": location,
                "experience": experience,
                "nignbevent_src": "jobsearchDeskGNB",
            }
            html = await self.fetch(f"{self.BASE_URL}/jobapi/v3/search", params=params)

        if not html:
            return []

        return self._parse(html, role, location)

    def _parse(self, html: str, role: str, location: str) -> list[JobListing]:
        jobs = []
        soup = BeautifulSoup(html, "lxml")

        cards = soup.find_all("article", class_=re.compile(r"jobTuple|srp-jobtuple"))
        if not cards:
            cards = soup.find_all("div", class_=re.compile(r"jobTuple|cust-job-tuple|list-container"))

        for card in cards:
            try:
                title_el = card.find("a", class_=re.compile(r"title|desig"))
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                company_el = card.find("a", class_=re.compile(r"comp-name|subTitle"))
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                loc_el = card.find(class_=re.compile(r"loc[_-]|location"))
                loc = loc_el.get_text(strip=True) if loc_el else location

                exp_el = card.find(class_=re.compile(r"exp[_-]|experience"))
                exp = exp_el.get_text(strip=True) if exp_el else ""

                salary_el = card.find(class_=re.compile(r"sal[_-]|salary"))
                salary = salary_el.get_text(strip=True) if salary_el else ""

                link = title_el if title_el and title_el.get("href") else card.find("a", href=True)
                url = ""
                
                # Naukri job ID
                real_job_id = card.get("data-job-id") or ""
                if not real_job_id and link and link.get("href"):
                    match = re.search(r"-(\d{6,})", link.get("href"))
                    if match:
                        real_job_id = match.group(1)

                if real_job_id:
                    role_slug = quote_plus(title.lower().replace(" ", "-").replace("/", ""))
                    url = f"{self.BASE_URL}/job-listings-{role_slug}-{real_job_id}"
                elif link:
                    href = link.get("href", "")
                    if href.startswith("http"):
                        url = href
                    elif href:
                        url = f"{self.BASE_URL}{href if href.startswith('/') else '/' + href}"
                
                if not url or url == f"{self.BASE_URL}/" or url.endswith("/jobs/"):
                    role_slug = quote_plus(title.lower().replace(" ", "-") or "jobs")
                    loc_slug = quote_plus(loc.lower().replace(" ", "-") or "india")
                    url = f"{self.BASE_URL}/{role_slug}-jobs-in-{loc_slug}"

                # Skills
                skills = []
                skill_els = card.find_all(class_=re.compile(r"tag|skill"))
                for s in skill_els:
                    skills.append(s.get_text(strip=True))

                job_id = hashlib.md5(f"naukri_{title}_{company}".encode()).hexdigest()[:12]

                jobs.append(JobListing(
                    id=f"nk_{job_id}",
                    title=title,
                    company=company,
                    location=loc,
                    salary=salary,
                    experience=exp,
                    skills=skills,
                    url=url,
                    platform="naukri",
                ))
            except Exception as e:
                log.debug(f"[Naukri] Parse error: {e}")
                continue

        log.info(f"[Naukri] Found {len(jobs)} jobs for '{role}' in '{location}'")
        return jobs

    async def get_job_details(self, job_id: str) -> Optional[JobListing]:
        return None
