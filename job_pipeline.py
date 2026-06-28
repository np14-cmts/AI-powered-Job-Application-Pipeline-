"""
AI Job Application Pipeline
Searches LinkedIn & Naukri for Senior PM jobs, runs Claude fitment analysis,
exports ranked Excel report, and opens top matches in browser.

Setup:
    pip install anthropic playwright openpyxl requests beautifulsoup4 rich
    playwright install chromium
"""

import os
import re
import time
import json
import webbrowser
import anthropic
from datetime import datetime
from playwright.sync_api import sync_playwright
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

console = Console()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

RESUME = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. Proven track record of leading cross-functional teams of 30+
members, delivering projects worth ₹50Cr+ on time and within budget. Expertise in
Agile, Scrum, Waterfall, PMP-certified, stakeholder management, risk mitigation,
and vendor negotiations. Managed multi-site projects across Bengaluru and Coimbatore.
Strong in JIRA, MS Project, and C-level executive reporting.
"""

JOB_TITLE    = "Senior Project Manager"
LOCATIONS    = ["Bengaluru", "Coimbatore"]
MAX_JOBS     = 15          # total jobs to scrape across both portals
TOP_N_OPEN   = 5           # top N matches to auto-open in browser
MIN_FIT_PCT  = 50          # skip jobs below this fitment threshold
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

# ─── SCRAPER ─────────────────────────────────────────────────────────────────

def scrape_linkedin(page, title, location, max_results=8):
    jobs = []
    loc_query = location.replace(" ", "%20")
    title_query = title.replace(" ", "%20")
    url = f"https://www.linkedin.com/jobs/search/?keywords={title_query}&location={loc_query}&f_TPR=r604800"
    console.log(f"[cyan]LinkedIn:[/cyan] {url}")
    try:
        page.goto(url, timeout=20000)
        page.wait_for_timeout(3000)
        cards = page.query_selector_all(".job-search-card")
        for card in cards[:max_results]:
            try:
                title_el  = card.query_selector(".base-search-card__title")
                company   = card.query_selector(".base-search-card__subtitle")
                loc_el    = card.query_selector(".job-search-card__location")
                link_el   = card.query_selector("a.base-card__full-link")
                jobs.append({
                    "portal":   "LinkedIn",
                    "title":    title_el.inner_text().strip()  if title_el  else title,
                    "company":  company.inner_text().strip()   if company   else "Unknown",
                    "location": loc_el.inner_text().strip()    if loc_el    else location,
                    "url":      link_el.get_attribute("href")  if link_el   else url,
                    "jd":       ""
                })
            except Exception:
                continue
    except Exception as e:
        console.log(f"[yellow]LinkedIn scrape warning:[/yellow] {e}")
    return jobs


def scrape_naukri(page, title, location, max_results=8):
    jobs = []
    loc_query   = location.lower().replace(" ", "-")
    title_query = title.lower().replace(" ", "-")
    url = f"https://www.naukri.com/{title_query}-jobs-in-{loc_query}"
    console.log(f"[cyan]Naukri:[/cyan] {url}")
    try:
        page.goto(url, timeout=20000)
        page.wait_for_timeout(3000)
        cards = page.query_selector_all(".srp-jobtuple-wrapper, article.jobTuple")
        for card in cards[:max_results]:
            try:
                title_el  = card.query_selector(".title, .jobTitle")
                company   = card.query_selector(".comp-name, .companyName")
                loc_el    = card.query_selector(".locWdth, .location")
                link_el   = card.query_selector("a.title, a.jobTitle")
                jobs.append({
                    "portal":   "Naukri",
                    "title":    title_el.inner_text().strip()            if title_el  else title,
                    "company":  company.inner_text().strip()             if company   else "Unknown",
                    "location": loc_el.inner_text().strip()              if loc_el    else location,
                    "url":      link_el.get_attribute("href")            if link_el   else url,
                    "jd":       ""
                })
            except Exception:
                continue
    except Exception as e:
        console.log(f"[yellow]Naukri scrape warning:[/yellow] {e}")
    return jobs


def fetch_jd(page, url):
    """Fetch JD text from a job detail page."""
    try:
        page.goto(url, timeout=15000)
        page.wait_for_timeout(2000)
        # LinkedIn
        jd_el = page.query_selector(".show-more-less-html__markup, .description__text")
        if jd_el:
            return jd_el.inner_text().strip()[:3000]
        # Naukri
        jd_el = page.query_selector(".job-desc, .JDC, #job-desc")
        if jd_el:
            return jd_el.inner_text().strip()[:3000]
        # Generic fallback — grab main body text
        body = page.query_selector("main, article, #content, body")
        return body.inner_text().strip()[:3000] if body else ""
    except Exception:
        return ""

# ─── CLAUDE FITMENT ──────────────────────────────────────────────────────────

def run_fitment(client, job, resume):
    """Call Claude to score resume vs JD."""
    if not job["jd"] or len(job["jd"]) < 50:
        job["jd"] = f"Senior Project Manager role at {job['company']} in {job['location']}. Requires project management experience, stakeholder management, and team leadership."

    prompt = f"""You are a resume fitment analyzer. Analyze strictly and reply ONLY in this exact format:

FIT:{{}number 0-100}}
MATCHES:skill1,skill2,skill3
GAPS:gap1,gap2,gap3
VERDICT:one sentence recommendation

Resume:
{resume.strip()}

Job Title: {job['title']}
Company: {job['company']}
Job Description:
{job['jd'][:2000]}"""

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        r = msg.content[0].text
        fit      = int((re.search(r"FIT:(\d+)", r) or [None, 0])[1])
        matches  = (re.search(r"MATCHES:(.+)",  r) or [None, ""])[1].strip()
        gaps     = (re.search(r"GAPS:(.+)",     r) or [None, ""])[1].strip()
        verdict  = (re.search(r"VERDICT:(.+)",  r) or [None, ""])[1].strip()
        return fit, matches, gaps, verdict
    except Exception as e:
        return 0, "", "", f"Error: {e}"

# ─── EXCEL REPORT ────────────────────────────────────────────────────────────

def build_excel(results, output_path):
    wb = Workbook()

    # ── Summary sheet ──
    ws = wb.active
    ws.title = "Fitment Report"

    # Header row
    headers = ["#", "Portal", "Company", "Job Title", "Location",
               "Fit %", "Matched Skills", "Skill Gaps", "Verdict", "Apply Link"]
    header_fill   = PatternFill("solid", fgColor="1F4E79")
    header_font   = Font(bold=True, color="FFFFFF", name="Arial", size=10)
    center        = Alignment(horizontal="center", vertical="center", wrap_text=True)
    wrap          = Alignment(vertical="top", wrap_text=True)
    thin          = Side(style="thin", color="CCCCCC")
    border        = Border(left=thin, right=thin, top=thin, bottom=thin)

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font      = header_font
        cell.fill      = header_fill
        cell.alignment = center
        cell.border    = border

    ws.row_dimensions[1].height = 30

    # Data rows
    for i, r in enumerate(results, 2):
        fit = r["fit"]
        if   fit >= 85: row_fill = PatternFill("solid", fgColor="E2EFDA")
        elif fit >= 65: row_fill = PatternFill("solid", fgColor="FFEB9C")
        else:           row_fill = PatternFill("solid", fgColor="FFC7CE")

        values = [
            i - 1,
            r["portal"],
            r["company"],
            r["title"],
            r["location"],
            f"{fit}%",
            r["matches"],
            r["gaps"],
            r["verdict"],
            r["url"]
        ]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=i, column=col, value=val)
            cell.fill      = row_fill
            cell.border    = border
            cell.font      = Font(name="Arial", size=9)
            cell.alignment = center if col in (1, 6) else wrap
            if col == 10:
                cell.font = Font(name="Arial", size=9, color="0070C0", underline="single")

    # Column widths
    widths = [4, 10, 22, 28, 16, 7, 35, 30, 40, 50]
    for col, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    # ── Stats sheet ──
    ws2 = wb.create_sheet("Summary Stats")
    ws2["A1"] = "AI Job Pipeline — Run Summary"
    ws2["A1"].font = Font(bold=True, size=14, name="Arial", color="1F4E79")
    ws2["A3"] = "Generated"
    ws2["B3"] = datetime.now().strftime("%d %b %Y, %H:%M")
    ws2["A4"] = "Total Jobs Analyzed"
    ws2["B4"] = f"=COUNTA('{ws.title}'!B2:B1000)"
    ws2["A5"] = "Strong Matches (≥85%)"
    ws2["B5"] = f"=COUNTIF('{ws.title}'!F2:F1000,\">=85%\")"
    ws2["A6"] = "Good Matches (65–84%)"
    ws2["B6"] = f"=COUNTIFS('{ws.title}'!F2:F1000,\">=65%\",'{ws.title}'!F2:F1000,\"<85%\")"
    ws2["A7"] = "Weak Matches (<65%)"
    ws2["B7"] = f"=COUNTIF('{ws.title}'!F2:F1000,\"<65%\")"
    ws2["A9"] = "Role"
    ws2["B9"] = JOB_TITLE
    ws2["A10"] = "Locations"
    ws2["B10"] = ", ".join(LOCATIONS)

    for row in range(3, 11):
        ws2.cell(row=row, column=1).font = Font(bold=True, name="Arial", size=10)
        ws2.cell(row=row, column=2).font = Font(name="Arial", size=10)

    ws2.column_dimensions["A"].width = 26
    ws2.column_dimensions["B"].width = 30

    wb.save(output_path)

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    console.rule("[bold blue]AI Job Application Pipeline[/bold blue]")
    console.print(f"Role: [bold]{JOB_TITLE}[/bold] | Locations: [bold]{', '.join(LOCATIONS)}[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set your Anthropic API key in ANTHROPIC_KEY env variable or in this script.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    all_jobs = []

    # ── Scrape jobs ──
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ))
        page = context.new_page()

        console.print("[bold cyan]Step 1 — Scraping job listings...[/bold cyan]")
        per_portal = MAX_JOBS // (2 * len(LOCATIONS))

        for loc in LOCATIONS:
            all_jobs += scrape_linkedin(page, JOB_TITLE, loc, per_portal)
            all_jobs += scrape_naukri(page, JOB_TITLE, loc, per_portal)

        console.print(f"Found [bold]{len(all_jobs)}[/bold] job listings. Fetching JDs...")

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as prog:
            task = prog.add_task("Fetching job descriptions...", total=len(all_jobs))
            for job in all_jobs:
                prog.update(task, description=f"Fetching JD: {job['company'][:30]}")
                job["jd"] = fetch_jd(page, job["url"])
                prog.advance(task)
                time.sleep(0.5)

        browser.close()

    # ── Run fitment ──
    console.print(f"\n[bold cyan]Step 2 — Running Claude fitment analysis on {len(all_jobs)} jobs...[/bold cyan]")
    results = []

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as prog:
        task = prog.add_task("Analyzing...", total=len(all_jobs))
        for job in all_jobs:
            prog.update(task, description=f"Analyzing: {job['company'][:35]}")
            fit, matches, gaps, verdict = run_fitment(client, job, RESUME)
            if fit >= MIN_FIT_PCT:
                results.append({**job, "fit": fit, "matches": matches, "gaps": gaps, "verdict": verdict})
            prog.advance(task)
            time.sleep(0.3)

    # Sort by fitment descending
    results.sort(key=lambda x: x["fit"], reverse=True)

    # ── Print summary table ──
    console.print(f"\n[bold green]✓ {len(results)} jobs above {MIN_FIT_PCT}% fitment threshold[/bold green]\n")
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#",        width=3)
    table.add_column("Fit",      width=6)
    table.add_column("Company",  width=22)
    table.add_column("Location", width=14)
    table.add_column("Portal",   width=9)
    table.add_column("Verdict",  width=45)

    for i, r in enumerate(results[:10], 1):
        fit_str = f"[green]{r['fit']}%[/green]" if r["fit"] >= 85 else \
                  f"[yellow]{r['fit']}%[/yellow]" if r["fit"] >= 65 else \
                  f"[red]{r['fit']}%[/red]"
        table.add_row(str(i), fit_str, r["company"][:22], r["location"][:14], r["portal"], r["verdict"][:45])

    console.print(table)

    # ── Export Excel ──
    out_path = f"job_fitment_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    build_excel(results, out_path)
    console.print(f"\n[bold green]✓ Excel report saved:[/bold green] {out_path}")

    # ── Open top N in browser ──
    top = [r for r in results if r["fit"] >= 75][:TOP_N_OPEN]
    if top:
        console.print(f"\n[bold cyan]Opening top {len(top)} matches in browser...[/bold cyan]")
        for r in top:
            webbrowser.open(r["url"])
            time.sleep(0.8)
        console.print("[green]Done! Check your browser tabs.[/green]")

    console.rule("[bold blue]Pipeline Complete[/bold blue]")


if __name__ == "__main__":
    main()
