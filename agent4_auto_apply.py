"""
agent4_auto_apply.py — Agent 4: Auto-Apply Strategy
Generates a complete application strategy and opens top job URLs in browser.

Usage:
    python agent4_auto_apply.py
"""

import os
import time
import webbrowser
import anthropic
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

console = Console()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

JOB_TITLE  = "Senior Project Manager"
LOCATIONS  = ["Bengaluru", "Coimbatore"]
YEARS_EXP  = "20"
SKILLS     = "PMP, Agile, Scrum, Waterfall, JIRA, MS Project, stakeholder management, vendor management, C-level reporting"
SALARY_RANGE = "₹40–60 LPA"

# Direct job search URLs — these open instantly in your browser
JOB_URLS = {
    "LinkedIn — Senior PM Bengaluru":
        "https://www.linkedin.com/jobs/search/?keywords=Senior+Project+Manager&location=Bengaluru&f_TPR=r604800&f_E=4%2C5",
    "LinkedIn — Senior PM Coimbatore":
        "https://www.linkedin.com/jobs/search/?keywords=Senior+Project+Manager&location=Coimbatore&f_TPR=r604800",
    "Naukri — Senior PM Bengaluru":
        "https://www.naukri.com/senior-project-manager-jobs-in-bengaluru",
    "Naukri — Senior PM Coimbatore":
        "https://www.naukri.com/senior-project-manager-jobs-in-coimbatore",
    "Foundit (Monster) — Senior PM":
        "https://www.foundit.in/srp/results?query=Senior+Project+Manager&locations=Bengaluru%2CCoimbatore",
    "Indeed India — Senior PM":
        "https://in.indeed.com/jobs?q=Senior+Project+Manager&l=Bengaluru%2C+Karnataka",
    "Instahyre — Senior PM":
        "https://www.instahyre.com/search-jobs/?designation=Senior+Project+Manager&city=Bengaluru",
    "IIMJobs — Senior PM":
        "https://www.iimjobs.com/j/senior-project-manager-jobs.html",
}

# ─── AGENT ───────────────────────────────────────────────────────────────────

def run_auto_apply_agent():
    console.rule("[bold blue]Agent 4 — Auto-Apply Strategy[/bold blue]")
    console.print(f"Role: [bold]{JOB_TITLE}[/bold] | Locations: [bold]{', '.join(LOCATIONS)}[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set your ANTHROPIC_KEY in environment or in this script.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = f"""You are a senior career strategist specializing in IT project management roles in India.

Candidate Profile:
- Role: {JOB_TITLE}
- Experience: {YEARS_EXP} years
- Locations: {', '.join(LOCATIONS)}
- Key Skills: {SKILLS}
- Target Salary: {SALARY_RANGE}

Create a detailed, actionable auto-apply strategy:

PORTAL_STRATEGY:
For each of these portals — LinkedIn, Naukri, Foundit, Indeed India, IIMJobs, Instahyre — give:
  - Best search keywords to use
  - Filters to apply (experience, salary, date posted)
  - One insider tip to get more responses

DAILY_SCHEDULE:
[A realistic 5-day per week application schedule with time blocks and daily targets]

PROFILE_OPTIMIZATION:
[5 specific tips to optimize LinkedIn and Naukri profiles for this role]

RECRUITER_OUTREACH:
[List 5 types of recruiters/agencies in Bengaluru and Coimbatore that specialize in PM roles, with how to approach them]

ATS_KEYWORDS:
[20 ATS keywords to include in resume and applications for {JOB_TITLE} roles in India]

RED_FLAGS_TO_AVOID:
[5 common mistakes senior candidates make when applying online]

FOLLOW_UP_STRATEGY:
[Exact steps to follow up after applying — timing, channel, what to say]
"""

    console.print("[cyan]Generating apply strategy with Claude...[/cyan]\n")

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text

        console.print(Panel(result, title="[bold green]Auto-Apply Strategy[/bold green]", border_style="green"))

        # Job portal table
        console.print("\n")
        table = Table(title="Job Portals — Ready to Open", show_header=True, header_style="bold blue")
        table.add_column("#",       width=3)
        table.add_column("Portal",  width=40)
        table.add_column("URL",     width=70)
        for i, (name, url) in enumerate(JOB_URLS.items(), 1):
            table.add_row(str(i), name, url)
        console.print(table)

        # Save strategy to file
        out_file = f"apply_strategy_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"AUTO-APPLY STRATEGY — {JOB_TITLE}\n")
            f.write(f"Locations: {', '.join(LOCATIONS)} | Generated: {datetime.now().strftime('%d %b %Y %H:%M')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(result)
            f.write("\n\n" + "=" * 70 + "\n")
            f.write("JOB PORTAL URLs\n")
            f.write("=" * 70 + "\n")
            for name, url in JOB_URLS.items():
                f.write(f"\n{name}\n{url}\n")

        console.print(f"\n[green]✓ Strategy saved to:[/green] {out_file}")

        # Open in browser
        if Confirm.ask("\nOpen all job portal URLs in your browser now?"):
            console.print("[cyan]Opening job portals...[/cyan]")
            for name, url in JOB_URLS.items():
                console.print(f"  Opening: {name}")
                webbrowser.open(url)
                time.sleep(1.0)
            console.print("[green]✓ All portals opened! Start applying.[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    run_auto_apply_agent()
