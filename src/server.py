"""
Job Application MCP Server
===========================
An MCP (Model Context Protocol) server that provides AI-powered job search,
matching, and application tracking tools.

Tools:
  - search_jobs: Search across LinkedIn, Indeed, Glassdoor, Naukri, Internshala
  - analyze_job: AI-analyze how well a job matches your profile
  - rank_jobs: Rank all found jobs by match score
  - generate_cover_letter: Create a tailored cover letter for a job
  - resume_tips: Get resume optimization tips for a specific job
  - track_application: Record a job application
  - application_stats: View application tracking dashboard
  - list_jobs: View all cached job results

Resources:
  - profile://info: Your profile/resume summary
  - jobs://cached: All cached job listings
  - stats://applications: Application statistics
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .engine import JobEngine
from .utils.logger import log


# ── Create MCP Server ──
mcp = FastMCP(
    name="job-apply",
    instructions="""You are a job application assistant for Al Mahaboob Phyas, a B.Tech AI & Data Science fresher.
You help search for jobs, analyze job-profile fit, generate cover letters, and track applications.
Always be helpful, proactive, and suggest next steps after each action.
When showing jobs, include the match score and direct URL when available.
Prioritize AI/ML, Data Science, Python, and Software Engineering roles.""",
)

# ── Global engine instance ──
engine: JobEngine = None


def get_engine() -> JobEngine:
    global engine
    if engine is None:
        engine = JobEngine()
    return engine


# ═══════════════════════════════════════════
#                  TOOLS
# ═══════════════════════════════════════════

@mcp.tool()
async def search_jobs(
    roles: str = "AI ML Engineer, Python Developer, Data Scientist, Software Engineer",
    locations: str = "Remote, Chennai, Bangalore, Hyderabad",
    platforms: str = "linkedin, indeed, naukri, glassdoor, internshala",
    experience: str = "fresher",
    posted_within: str = "7d",
    max_per_platform: int = 15,
) -> str:
    """Search for jobs across multiple platforms simultaneously.

    Args:
        roles: Comma-separated job titles to search for
        locations: Comma-separated locations to search in
        platforms: Comma-separated platforms (linkedin, indeed, naukri, glassdoor, internshala)
        experience: Experience level - fresher, entry, mid, senior
        posted_within: Time filter - 24h, 3d, 7d, 14d, 30d
        max_per_platform: Maximum jobs to fetch per platform

    Returns:
        Summary of jobs found with counts per platform
    """
    eng = get_engine()

    role_list = [r.strip() for r in roles.split(",")]
    loc_list = [l.strip() for l in locations.split(",")]
    plat_list = [p.strip() for p in platforms.split(",")]

    jobs = await eng.search_jobs(
        roles=role_list,
        locations=loc_list,
        platforms=plat_list,
        experience=experience,
        posted_within=posted_within,
        max_per_platform=max_per_platform,
    )

    if not jobs:
        return "No jobs found. Try broadening your search criteria or different platforms."

    # Group by platform
    by_platform = {}
    for j in jobs:
        by_platform.setdefault(j.platform, []).append(j)

    summary = f"## Found {len(jobs)} Jobs\n\n"
    for platform, pjobs in by_platform.items():
        summary += f"### {platform.title()} ({len(pjobs)} jobs)\n"
        for j in pjobs[:10]:
            summary += f"- **{j.title}** @ {j.company} ({j.location})"
            if j.salary:
                summary += f" | {j.salary}"
            if j.url:
                summary += f" | [Link]({j.url})"
            summary += f" `ID: {j.id}`\n"
        if len(pjobs) > 10:
            summary += f"  _...and {len(pjobs) - 10} more_\n"
        summary += "\n"

    summary += "\n**Next steps:** Use `analyze_job` with a job ID to check match score, or `rank_jobs` to rank all jobs."
    return summary


@mcp.tool()
async def analyze_job(job_id: str) -> str:
    """Analyze how well a specific job matches your profile using Gemini AI.

    Args:
        job_id: The job ID from search results (e.g., li_abc123, nk_def456)

    Returns:
        Detailed match analysis with score, matching/missing skills, and recommendation
    """
    eng = get_engine()
    result = await eng.analyze_job(job_id)

    if "error" in result:
        return result["error"]

    output = f"""## Job Match Analysis

**Job:** {result['job']}
**URL:** {result.get('url', 'N/A')}
**Match Score:** {result['match_score']}/100 {'🟢' if result['match_score'] >= 70 else '🟡' if result['match_score'] >= 50 else '🔴'}

### Matching Skills
{', '.join(result['matching_skills']) or 'None identified'}

### Missing Skills
{', '.join(result['missing_skills']) or 'None - great fit!'}

### Recommendation
{result['recommendation']}

### Tailored Summary
{result.get('tailored_summary', 'N/A')}

**Next:** Use `generate_cover_letter` for this job ID, or `track_application` to mark it applied."""
    return output


@mcp.tool()
async def rank_jobs(min_score: float = 40) -> str:
    """Rank all cached jobs by AI match score. Analyzes each job against your profile.

    Args:
        min_score: Minimum match score to include (0-100)

    Returns:
        Ranked list of jobs with match scores
    """
    eng = get_engine()
    results = await eng.analyze_all_jobs(min_score=min_score)

    if not results or (len(results) == 1 and "error" in results[0]):
        return results[0].get("error", "No jobs to rank.") if results else "No jobs cached."

    output = f"## Job Rankings (min score: {min_score})\n\n"
    output += f"| Rank | Score | Title | Company | Platform | Link |\n"
    output += f"|------|-------|-------|---------|----------|------|\n"

    for i, r in enumerate(results, 1):
        score_emoji = '🟢' if r['match_score'] >= 70 else '🟡' if r['match_score'] >= 50 else '🔴'
        url_link = f"[Apply]({r['url']})" if r.get('url') else "N/A"
        output += f"| {i} | {score_emoji} {r['match_score']} | {r['title'][:35]} | {r['company'][:20]} | {r['platform']} | {url_link} |\n"

    output += f"\n**Total: {len(results)} jobs above {min_score}% match**"
    return output


@mcp.tool()
async def generate_cover_letter(job_id: str) -> str:
    """Generate an AI-tailored cover letter for a specific job.

    Args:
        job_id: The job ID to generate a cover letter for

    Returns:
        A professional, tailored cover letter
    """
    eng = get_engine()
    return await eng.get_cover_letter(job_id)


@mcp.tool()
async def resume_tips(job_id: str) -> str:
    """Get AI-powered resume optimization tips tailored for a specific job.

    Args:
        job_id: The job ID to optimize your resume for

    Returns:
        Specific suggestions for keywords, skills to highlight, and resume tweaks
    """
    eng = get_engine()
    return await eng.get_resume_tips(job_id)


@mcp.tool()
def track_application(job_id: str, status: str = "applied", notes: str = "") -> str:
    """Track a job application in your application log.

    Args:
        job_id: The job ID being applied to
        status: Application status - pending, applied, rejected, interview, offer
        notes: Optional notes about the application

    Returns:
        Confirmation message with total application count
    """
    eng = get_engine()
    result = eng.track_application(job_id, status, notes)
    if "error" in result:
        return result["error"]
    return f"✅ {result['message']}\n📊 Total applications tracked: {result['total_applications']}"


@mcp.tool()
def application_stats() -> str:
    """View your job application tracking dashboard.

    Returns:
        Statistics including total applications, status breakdown, and recent activity
    """
    eng = get_engine()
    stats = eng.get_application_stats()

    if stats["total"] == 0:
        return "No applications tracked yet. Use `track_application` after applying to a job."

    output = f"## Application Dashboard\n\n"
    output += f"**Total Applications:** {stats['total']}\n\n"

    output += "### By Status\n"
    for status, count in stats["by_status"].items():
        output += f"- **{status.title()}:** {count}\n"

    output += "\n### By Platform\n"
    for platform, count in stats["by_platform"].items():
        output += f"- **{platform.title()}:** {count}\n"

    output += "\n### Recent Applications\n"
    for app in stats["recent"]:
        output += f"- {app['title']} @ {app['company']} | {app['status']} | {app['platform']} | {app['date']}\n"

    return output


@mcp.tool()
def list_jobs(platform: str = "") -> str:
    """List all cached jobs from the most recent search.

    Args:
        platform: Optional filter by platform name (linkedin, indeed, etc.)

    Returns:
        Table of all cached jobs with IDs for use in other tools
    """
    eng = get_engine()
    jobs = eng.list_cached_jobs(platform=platform if platform else None)

    if not jobs:
        return "No jobs cached. Run `search_jobs` first."

    output = f"## Cached Jobs ({len(jobs)} total)\n\n"
    for j in jobs:
        score_str = f" | Score: {j['match_score']}" if j['match_score'] > 0 else ""
        output += f"- `{j['id']}` **{j['title']}** @ {j['company']} ({j['platform']}){score_str}\n"

    return output


# ═══════════════════════════════════════════
#                RESOURCES
# ═══════════════════════════════════════════

@mcp.resource("profile://info")
def get_profile() -> str:
    """Returns the user's profile/resume summary."""
    profile_path = Path(__file__).parent.parent / "data" / "profile.json"
    if profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        return json.dumps(profile, indent=2)
    return "Profile not found. Please add data/profile.json"


@mcp.resource("jobs://cached")
def get_cached_jobs() -> str:
    """Returns all cached job listings."""
    eng = get_engine()
    jobs = eng.list_cached_jobs()
    return json.dumps(jobs, indent=2)


@mcp.resource("stats://applications")
def get_stats() -> str:
    """Returns application tracking statistics."""
    eng = get_engine()
    return json.dumps(eng.get_application_stats(), indent=2)


# ═══════════════════════════════════════════
#                PROMPTS
# ═══════════════════════════════════════════

@mcp.prompt()
def daily_job_hunt() -> str:
    """A prompt for daily job hunting workflow."""
    return """Please help me with my daily job search:

1. Search for fresh jobs posted in the last 24 hours for my target roles (AI/ML Engineer, Data Scientist, Python Developer, Software Engineer) in Remote, Chennai, Bangalore, and Hyderabad.
2. Rank all found jobs by match score.
3. For the top 3 matches, show me detailed analysis.
4. Generate a cover letter for the best match.
5. Show my application stats.

Let's go!"""


@mcp.prompt()
def quick_search(role: str = "AI ML Engineer", location: str = "Remote") -> str:
    """Quick search for a specific role and location."""
    return f"Search for {role} jobs in {location} across all platforms, then rank them by match score and show me the top 5."


# ═══════════════════════════════════════════
#                  MAIN
# ═══════════════════════════════════════════

def main():
    """Run the MCP server."""
    log.info("Starting Job Application MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
