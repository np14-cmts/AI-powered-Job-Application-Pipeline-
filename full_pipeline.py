"""
full_pipeline.py — Complete AI Job Application Pipeline
Searches LinkedIn + Naukri → scrapes JDs → runs ALL 6 agents
per company automatically → exports one master Excel report.

Usage:
    python full_pipeline.py
"""

import os
import re
import time
import webbrowser
import anthropic
from datetime import datetime
from playwright.sync_api import sync_playwright
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

# ─── CONFIG — Edit this section only ─────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

# Use Haiku for cost savings ($1/M vs $3/M) — change to claude-sonnet-4-6 for better quality
MODEL = "claude-haiku-4-5-20251001"

RESUME = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. Proven track record of leading cross-functional teams of 30+
members, delivering projects worth ₹50Cr+ on time and within budget. PMP-certified.
Expertise in Agile, Scrum, Waterfall, stakeholder management, risk mitigation,
vendor negotiations, and C-level executive reporting. Managed multi-site projects
across Bengaluru and Coimbatore. Proficient in JIRA, MS Project, Confluence.
"""

YOUR_NAME    = "Your Full Name"
YOUR_EMAIL   = "your.email@example.com"
YOUR_PHONE   = "+91-XXXXXXXXXX"
YOUR_LINKEDIN = "linkedin.com/in/yourprofile"

JOB_TITLE    = "Senior Project Manager"
LOCATIONS    = ["Bengaluru", "Coimbatore"]
YEARS_EXP    = "20"
MAX_JOBS     = 20       # Total jobs to scrape across LinkedIn + Naukri
TOP_MATCHES  = 5        # Run full agents only on top N matches
MIN_FIT_PCT  = 60       # Skip jobs below this fitment %

SEARCH_LINKEDIN = True
SEARCH_NAUKRI   = True

# ─── SCRAPER ─────────────────────────────────────────────────────────────────

def scrape_linkedin(page, title, location, max_results=6):
    jobs = []
    url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={title.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        f"&f_TPR=r604800&sortBy=DD"
    )
    console.log(f"[cyan]LinkedIn → {location}[/cyan]")
    try:
        page.goto(url, timeout=25000)
        page.wait_for_timeout(3000)
        cards = page.query_selector_all(".job-search-card")
        for card in cards[:max_results]:
            try:
                jobs.append({
                    "portal":   "LinkedIn",
                    "title":    _text(card, ".base-search-card__title") or title,
                    "company":  _text(card, ".base-search-card__subtitle") or "Unknown",
                    "location": _text(card, ".job-search-card__location") or location,
                    "url":      _href(card, "a.base-card__full-link") or url,
                    "jd":       "",
                    "fit":      0,
                    "matches":  "",
                    "gaps":     "",
                    "verdict":  "",
                    "resume":   "",
                    "cover":    "",
                    "outreach": "",
                    "interview":"",
                })
            except Exception:
                continue
    except Exception as e:
        console.log(f"[yellow]LinkedIn warning:[/yellow] {e}")
    return jobs


def scrape_naukri(page, title, location, max_results=6):
    jobs = []
    url = (
        f"https://www.naukri.com/"
        f"{title.lower().replace(' ', '-')}-jobs-in-"
        f"{location.lower().replace(' ', '-')}"
    )
    console.log(f"[cyan]Naukri → {location}[/cyan]")
    try:
        page.goto(url, timeout=25000)
        page.wait_for_timeout(3000)
        cards = page.query_selector_all(".srp-jobtuple-wrapper, article.jobTuple")
        for card in cards[:max_results]:
            try:
                jobs.append({
                    "portal":   "Naukri",
                    "title":    _text(card, ".title, .jobTitle") or title,
                    "company":  _text(card, ".comp-name, .companyName") or "Unknown",
                    "location": _text(card, ".locWdth, .location") or location,
                    "url":      _href(card, "a.title, a.jobTitle") or url,
                    "jd":       "",
                    "fit":      0,
                    "matches":  "",
                    "gaps":     "",
                    "verdict":  "",
                    "resume":   "",
                    "cover":    "",
                    "outreach": "",
                    "interview":"",
                })
            except Exception:
                continue
    except Exception as e:
        console.log(f"[yellow]Naukri warning:[/yellow] {e}")
    return jobs


def fetch_jd(page, url):
    try:
        page.goto(url, timeout=15000)
        page.wait_for_timeout(2000)
        for sel in [
            ".show-more-less-html__markup", ".description__text",
            ".job-desc", ".JDC", "#job-desc", "main", "article"
        ]:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if len(text) > 100:
                    return text[:3000]
    except Exception:
        pass
    return ""


def _text(el, selector):
    found = el.query_selector(selector)
    return found.inner_text().strip() if found else None


def _href(el, selector):
    found = el.query_selector(selector)
    return found.get_attribute("href") if found else None

# ─── AGENT 2: FITMENT ────────────────────────────────────────────────────────

def agent2_fitment(client, job):
    jd = job["jd"] or f"Senior PM role at {job['company']} in {job['location']}."
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=[{"role": "user", "content": f"""Analyze resume vs JD. Reply ONLY in this format:
FIT:{{0-100}}
MATCHES:skill1,skill2,skill3
GAPS:gap1,gap2,gap3
VERDICT:one sentence

Resume: {RESUME.strip()}
Company: {job['company']}
JD: {jd[:2000]}"""}]
        )
        r = msg.content[0].text
        job["fit"]     = int((re.search(r"FIT:(\d+)", r) or [None, 0])[1])
        job["matches"] = (re.search(r"MATCHES:(.+)", r) or [None, ""])[1].strip()
        job["gaps"]    = (re.search(r"GAPS:(.+)",    r) or [None, ""])[1].strip()
        job["verdict"] = (re.search(r"VERDICT:(.+)", r) or [None, ""])[1].strip()
    except Exception as e:
        job["verdict"] = f"Error: {e}"
    return job

# ─── AGENT 3: RESUME REWRITE ─────────────────────────────────────────────────

def agent3_resume(client, job):
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": f"""Rewrite resume for this role. Plain text only.

SUMMARY: [2 sentences tailored to {job['company']}]
BULLETS:
1. [achievement with metric]
2. [achievement with metric]
3. [achievement with metric]
4. [achievement with metric]

Original resume: {RESUME.strip()}
Target: {JOB_TITLE} at {job['company']}
JD: {job['jd'][:1500]}"""}]
        )
        job["resume"] = msg.content[0].text.strip()
    except Exception as e:
        job["resume"] = f"Error: {e}"
    return job

# ─── AGENT 3B: COVER LETTER ──────────────────────────────────────────────────

def agent3_cover(client, job):
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": f"""Write a 3-paragraph cover letter.
- Open: hook with {YEARS_EXP} years experience
- Middle: 2 achievements matching {job['company']}'s JD
- Close: call to action
Sign off as {YOUR_NAME}.

Resume: {RESUME.strip()}
Company: {job['company']}
JD: {job['jd'][:1000]}"""}]
        )
        job["cover"] = msg.content[0].text.strip()
    except Exception as e:
        job["cover"] = f"Error: {e}"
    return job

# ─── AGENT 5: NETWORKING ─────────────────────────────────────────────────────

def agent5_outreach(client, job):
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=[{"role": "user", "content": f"""Write 2 LinkedIn messages for {job['company']}.

CONNECT: [connection request to HR/hiring manager, under 280 chars]
FOLLOWUP: [follow-up if no reply in 7 days, under 250 chars]

Candidate: {YOUR_NAME}, {YEARS_EXP} years PM experience, PMP certified.
Role: {JOB_TITLE} at {job['company']} in {job['location']}"""}]
        )
        job["outreach"] = msg.content[0].text.strip()
    except Exception as e:
        job["outreach"] = f"Error: {e}"
    return job

# ─── AGENT 6: INTERVIEW PREP ─────────────────────────────────────────────────

def agent6_interview(client, job):
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": f"""Generate interview prep for {job['company']}.

T1: [technical PM question]
T2: [methodology question]
B1: [behavioral question - STAR hint]
B2: [stakeholder management question]
SD: [case study/situational question]
ASK1: [smart question to ask interviewer]
ASK2: [smart question to ask interviewer]

Role: {JOB_TITLE} at {job['company']}
JD: {job['jd'][:1500]}"""}]
        )
        job["interview"] = msg.content[0].text.strip()
    except Exception as e:
        job["interview"] = f"Error: {e}"
    return job

# ─── EXCEL EXPORT ────────────────────────────────────────────────────────────

def build_excel(jobs, path):
    wb = Workbook()

    # ── Sheet 1: Fitment Rankings ─────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "Fitment Rankings"
    thin   = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    wrap   = Alignment(vertical="top", wrap_text=True)

    headers = ["Rank", "Fit%", "Company", "Portal", "Location",
               "Job Title", "Matched Skills", "Skill Gaps", "Verdict", "Apply URL"]
    for col, h in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=h)
        cell.font      = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        cell.fill      = PatternFill("solid", fgColor="1F4E79")
        cell.alignment = center
        cell.border    = border
    ws1.row_dimensions[1].height = 28

    for i, j in enumerate(jobs, 2):
        fit = j["fit"]
        fill = PatternFill("solid", fgColor=(
            "E2EFDA" if fit >= 85 else "FFEB9C" if fit >= 65 else "FFC7CE"
        ))
        row = [i-1, f"{fit}%", j["company"], j["portal"], j["location"],
               j["title"], j["matches"], j["gaps"], j["verdict"], j["url"]]
        for col, val in enumerate(row, 1):
            cell = ws1.cell(row=i, column=col, value=val)
            cell.fill      = fill
            cell.border    = border
            cell.font      = Font(name="Arial", size=9,
                                  color="0070C0" if col == 10 else "000000",
                                  underline="single" if col == 10 else None)
            cell.alignment = center if col in (1, 2) else wrap

    for col, w in enumerate([6,7,22,10,16,24,35,30,40,50], 1):
        ws1.column_dimensions[get_column_letter(col)].width = w
    ws1.freeze_panes = "A2"
    ws1.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    # ── Sheet 2: Tailored Resumes ─────────────────────────────────────────────
    ws2 = wb.create_sheet("Tailored Resumes")
    ws2.cell(row=1, column=1, value="Company").font = Font(bold=True, color="FFFFFF", name="Arial")
    ws2.cell(row=1, column=1).fill = PatternFill("solid", fgColor="1F4E79")
    ws2.cell(row=1, column=2, value="Fit%").font = Font(bold=True, color="FFFFFF", name="Arial")
    ws2.cell(row=1, column=2).fill = PatternFill("solid", fgColor="1F4E79")
    ws2.cell(row=1, column=3, value="Tailored Resume").font = Font(bold=True, color="FFFFFF", name="Arial")
    ws2.cell(row=1, column=3).fill = PatternFill("solid", fgColor="1F4E79")
    ws2.cell(row=1, column=4, value="Cover Letter").font = Font(bold=True, color="FFFFFF", name="Arial")
    ws2.cell(row=1, column=4).fill = PatternFill("solid", fgColor="1F4E79")

    top = [j for j in jobs if j.get("resume")]
    for i, j in enumerate(top, 2):
        ws2.cell(row=i, column=1, value=j["company"]).font = Font(bold=True, name="Arial", size=9)
        ws2.cell(row=i, column=2, value=f"{j['fit']}%").font = Font(name="Arial", size=9)
        ws2.cell(row=i, column=3, value=j.get("resume","")).font = Font(name="Arial", size=9)
        ws2.cell(row=i, column=3).alignment = wrap
        ws2.cell(row=i, column=4, value=j.get("cover","")).font = Font(name="Arial", size=9)
        ws2.cell(row=i, column=4).alignment = wrap
        ws2.row_dimensions[i].height = 120

    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 7
    ws2.column_dimensions["C"].width = 60
    ws2.column_dimensions["D"].width = 60

    # ── Sheet 3: Networking Messages ─────────────────────────────────────────
    ws3 = wb.create_sheet("Networking Messages")
    for col, h in enumerate(["Company", "Fit%", "LinkedIn Connect Message", "Follow-Up Message"], 1):
        ws3.cell(row=1, column=col, value=h).font = Font(bold=True, color="FFFFFF", name="Arial")
        ws3.cell(row=1, column=col).fill = PatternFill("solid", fgColor="1F4E79")

    for i, j in enumerate([x for x in jobs if x.get("outreach")], 2):
        outreach = j.get("outreach", "")
        connect  = (re.search(r"CONNECT:\s*(.+?)(?=FOLLOWUP:|$)", outreach, re.DOTALL) or [None,""])[1].strip()
        followup = (re.search(r"FOLLOWUP:\s*(.+?)$", outreach, re.DOTALL) or [None,""])[1].strip()
        ws3.cell(row=i, column=1, value=j["company"]).font = Font(bold=True, name="Arial", size=9)
        ws3.cell(row=i, column=2, value=f"{j['fit']}%").font = Font(name="Arial", size=9)
        ws3.cell(row=i, column=3, value=connect).alignment = wrap
        ws3.cell(row=i, column=3).font = Font(name="Arial", size=9)
        ws3.cell(row=i, column=4, value=followup).alignment = wrap
        ws3.cell(row=i, column=4).font = Font(name="Arial", size=9)
        ws3.row_dimensions[i].height = 80

    ws3.column_dimensions["A"].width = 22
    ws3.column_dimensions["B"].width = 7
    ws3.column_dimensions["C"].width = 55
    ws3.column_dimensions["D"].width = 55

    # ── Sheet 4: Interview Prep ───────────────────────────────────────────────
    ws4 = wb.create_sheet("Interview Prep")
    for col, h in enumerate(["Company", "Fit%", "Interview Questions & Prep"], 1):
        ws4.cell(row=1, column=col, value=h).font = Font(bold=True, color="FFFFFF", name="Arial")
        ws4.cell(row=1, column=col).fill = PatternFill("solid", fgColor="1F4E79")

    for i, j in enumerate([x for x in jobs if x.get("interview")], 2):
        ws4.cell(row=i, column=1, value=j["company"]).font = Font(bold=True, name="Arial", size=9)
        ws4.cell(row=i, column=2, value=f"{j['fit']}%").font = Font(name="Arial", size=9)
        ws4.cell(row=i, column=3, value=j.get("interview","")).alignment = wrap
        ws4.cell(row=i, column=3).font = Font(name="Arial", size=9)
        ws4.row_dimensions[i].height = 150

    ws4.column_dimensions["A"].width = 22
    ws4.column_dimensions["B"].width = 7
    ws4.column_dimensions["C"].width = 100

    # ── Sheet 5: Summary Stats ────────────────────────────────────────────────
    ws5 = wb.create_sheet("Summary")
    ws5["A1"] = "AI Job Pipeline — Master Report"
    ws5["A1"].font = Font(bold=True, size=14, name="Arial", color="1F4E79")
    stats = [
        ("Generated",              datetime.now().strftime("%d %b %Y, %H:%M")),
        ("Role",                   JOB_TITLE),
        ("Locations",              ", ".join(LOCATIONS)),
        ("Total Jobs Scraped",     str(len(jobs))),
        ("Above Threshold",        str(sum(1 for j in jobs if j["fit"] >= MIN_FIT_PCT))),
        ("Strong Matches (≥85%)",  str(sum(1 for j in jobs if j["fit"] >= 85))),
        ("Good Matches (65–84%)",  str(sum(1 for j in jobs if 65 <= j["fit"] < 85))),
        ("Weak Matches (<65%)",    str(sum(1 for j in jobs if j["fit"] < 65))),
        ("Full Agents Run On",     f"Top {TOP_MATCHES} companies"),
        ("Model Used",             MODEL),
    ]
    for row, (label, val) in enumerate(stats, 3):
        ws5.cell(row=row, column=1, value=label).font = Font(bold=True, name="Arial", size=10)
        ws5.cell(row=row, column=2, value=val).font   = Font(name="Arial", size=10)
    ws5.column_dimensions["A"].width = 28
    ws5.column_dimensions["B"].width = 35

    wb.save(path)

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    console.rule("[bold blue]AI Job Application Pipeline — Full Auto Mode[/bold blue]")
    console.print(f"Role: [bold]{JOB_TITLE}[/bold] | Locations: [bold]{', '.join(LOCATIONS)}[/bold] | Model: [bold]{MODEL}[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set ANTHROPIC_KEY in environment or in this script.")
        return

    client   = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    all_jobs = []
    per_loc  = max(2, MAX_JOBS // (2 * len(LOCATIONS)))

    # ── STEP 1: Scrape all jobs ──────────────────────────────────────────────
    console.print(Panel("[bold]Step 1 of 4[/bold] — Scraping LinkedIn + Naukri", style="cyan"))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )).new_page()

        for loc in LOCATIONS:
            if SEARCH_LINKEDIN:
                all_jobs += scrape_linkedin(page, JOB_TITLE, loc, per_loc)
            if SEARCH_NAUKRI:
                all_jobs += scrape_naukri(page, JOB_TITLE, loc, per_loc)

        console.print(f"Found [bold green]{len(all_jobs)}[/bold green] job listings — fetching JDs...")

        with Progress(SpinnerColumn(), TextColumn("{task.description}"),
                      BarColumn(), console=console) as prog:
            task = prog.add_task("Fetching JDs...", total=len(all_jobs))
            for job in all_jobs:
                prog.update(task, description=f"Fetching: {job['company'][:30]}")
                job["jd"] = fetch_jd(page, job["url"])
                prog.advance(task)
                time.sleep(0.3)

        browser.close()

    # ── STEP 2: Agent 2 — Fitment on ALL jobs ───────────────────────────────
    console.print(Panel(f"[bold]Step 2 of 4[/bold] — Agent 2: Fitment analysis on all {len(all_jobs)} companies", style="cyan"))

    with Progress(SpinnerColumn(), TextColumn("{task.description}"),
                  BarColumn(), console=console) as prog:
        task = prog.add_task("Analyzing...", total=len(all_jobs))
        for job in all_jobs:
            prog.update(task, description=f"Scoring: {job['company'][:35]}")
            agent2_fitment(client, job)
            prog.advance(task)
            time.sleep(0.2)

    # Sort by fitment
    all_jobs.sort(key=lambda x: x["fit"], reverse=True)
    qualified = [j for j in all_jobs if j["fit"] >= MIN_FIT_PCT]
    top_jobs  = qualified[:TOP_MATCHES]

    # Print ranked table
    console.print(f"\n[bold green]✓ Fitment complete — {len(qualified)} companies above {MIN_FIT_PCT}%[/bold green]\n")
    tbl = Table(show_header=True, header_style="bold blue", box=None)
    for col, w in [("#",3),("Fit%",6),("Company",22),("Portal",10),("Location",15),("Verdict",45)]:
        tbl.add_column(col, width=w)
    for i, j in enumerate(all_jobs[:12], 1):
        color = "green" if j["fit"] >= 85 else "yellow" if j["fit"] >= 65 else "red"
        tbl.add_row(str(i), f"[{color}]{j['fit']}%[/{color}]",
                    j["company"][:22], j["portal"], j["location"][:15], j["verdict"][:45])
    console.print(tbl)

    # ── STEP 3: Full agents on top N companies ───────────────────────────────
    console.print(Panel(
        f"[bold]Step 3 of 4[/bold] — Running Agents 3, 5, 6 on top {len(top_jobs)} companies:\n"
        + "\n".join(f"  • {j['company']} ({j['fit']}%)" for j in top_jobs),
        style="cyan"
    ))

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as prog:
        task = prog.add_task("Running agents...", total=len(top_jobs) * 4)

        for job in top_jobs:
            prog.update(task, description=f"Agent 3 (Resume): {job['company'][:30]}")
            agent3_resume(client, job)
            prog.advance(task)
            time.sleep(0.2)

            prog.update(task, description=f"Agent 3 (Cover letter): {job['company'][:30]}")
            agent3_cover(client, job)
            prog.advance(task)
            time.sleep(0.2)

            prog.update(task, description=f"Agent 5 (Networking): {job['company'][:30]}")
            agent5_outreach(client, job)
            prog.advance(task)
            time.sleep(0.2)

            prog.update(task, description=f"Agent 6 (Interview): {job['company'][:30]}")
            agent6_interview(client, job)
            prog.advance(task)
            time.sleep(0.2)

    # ── STEP 4: Export + Open browser ───────────────────────────────────────
    console.print(Panel("[bold]Step 4 of 4[/bold] — Exporting Excel + opening top matches", style="cyan"))

    out = f"job_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    build_excel(all_jobs, out)
    console.print(f"\n[bold green]✓ Master Excel report saved:[/bold green] {out}")
    console.print("   → Sheet 1: All companies ranked by fitment")
    console.print("   → Sheet 2: Tailored resumes per company")
    console.print("   → Sheet 3: LinkedIn outreach messages per company")
    console.print("   → Sheet 4: Interview prep per company")
    console.print("   → Sheet 5: Summary stats")

    # Save individual text files for top matches
    for job in top_jobs:
        safe = job["company"].replace(" ", "_").replace("/", "-")[:20]
        if job.get("resume"):
            with open(f"resume_{safe}.txt", "w", encoding="utf-8") as f:
                f.write(f"{YOUR_NAME} | {YOUR_EMAIL} | {YOUR_PHONE}\n\n")
                f.write(f"TARGET: {JOB_TITLE} at {job['company']}\n\n")
                f.write(job["resume"])
        if job.get("interview"):
            with open(f"interview_{safe}.txt", "w", encoding="utf-8") as f:
                f.write(f"INTERVIEW PREP — {job['company']}\n\n")
                f.write(job["interview"])

    console.print(f"\n[green]✓ Individual files saved for top {len(top_jobs)} companies[/green]")

    # Open top matches in browser
    if Confirm.ask(f"\nOpen top {len(top_jobs)} job URLs in browser?"):
        for job in top_jobs:
            console.print(f"  Opening: {job['company']} ({job['fit']}%)")
            webbrowser.open(job["url"])
            time.sleep(0.8)

    console.rule("[bold blue]Pipeline Complete[/bold blue]")
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • Scraped:        {len(all_jobs)} companies")
    console.print(f"  • Qualified:      {len(qualified)} above {MIN_FIT_PCT}%")
    console.print(f"  • Full prep done: Top {len(top_jobs)} companies")
    console.print(f"  • Excel:          {out}")
    console.print(f"  • Next step:      Open Excel → apply to green rows first!\n")


if __name__ == "__main__":
    main()
