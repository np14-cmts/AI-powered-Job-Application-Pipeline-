"""
agent5_networking.py — Agent 5: Networking Agent
Generates personalized LinkedIn outreach messages, referral requests,
and a complete networking strategy for your job search.

Usage:
    python agent5_networking.py
"""

import os
import anthropic
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

YOUR_NAME    = "Your Name"
JOB_TITLE    = "Senior Project Manager"
LOCATIONS    = ["Bengaluru", "Coimbatore"]
YEARS_EXP    = "20"
KEY_SKILLS   = "PMP, Agile, Scrum, JIRA, MS Project, stakeholder management, ₹50Cr+ budgets"
YOUR_CURRENT = "Senior Project Manager at XYZ Company"

RESUME_SUMMARY = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. PMP-certified. Led teams of 30+, delivered ₹50Cr+ projects
on time and within budget. Expert in Agile, Scrum, Waterfall, JIRA, MS Project,
vendor management, and C-level reporting across Bengaluru and Coimbatore.
"""

# ─── AGENT ───────────────────────────────────────────────────────────────────

def run_networking_agent():
    console.rule("[bold blue]Agent 5 — Networking Agent[/bold blue]")
    console.print(f"Generating outreach strategy for: [bold]{YOUR_NAME}[/bold] → [bold]{JOB_TITLE}[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set your ANTHROPIC_KEY in environment or in this script.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = f"""You are a professional networking coach for senior IT leaders in India.

Candidate: {YOUR_NAME}
Current Role: {YOUR_CURRENT}
Target Role: {JOB_TITLE}
Locations: {', '.join(LOCATIONS)}
Experience: {YEARS_EXP} years
Skills: {KEY_SKILLS}
Summary: {RESUME_SUMMARY.strip()}

Generate a complete networking kit with ALL of the following:

---
MESSAGE_1_CONNECTION_REQUEST:
[LinkedIn connection request to a hiring manager — under 280 characters. Personal, specific, not generic.]

---
MESSAGE_2_COLD_OUTREACH:
[Cold LinkedIn message to a CTO or VP of Engineering at a target company — under 450 characters. Lead with value, not need.]

---
MESSAGE_3_RECRUITER_OUTREACH:
[Message to a technical recruiter on LinkedIn — under 350 characters. Mention role, location, experience clearly.]

---
MESSAGE_4_REFERRAL_REQUEST:
[Message to a former colleague asking for a referral — under 400 characters. Warm, specific, makes it easy to say yes.]

---
MESSAGE_5_FOLLOW_UP:
[Follow-up message 7 days after no response to a connection request — under 300 characters. Polite, adds new value.]

---
MESSAGE_6_THANK_YOU_AFTER_CALL:
[Thank you message after an informational call — under 350 characters. Specific, references something from the call.]

---
LINKEDIN_HEADLINE:
[An optimized LinkedIn headline for {JOB_TITLE} with {YEARS_EXP} years experience — under 220 characters. Keyword-rich.]

---
LINKEDIN_ABOUT_SECTION:
[A compelling LinkedIn About section — 3 paragraphs. Opens with a hook, highlights top 3 achievements with metrics, ends with what you're looking for.]

---
NETWORKING_STRATEGY:
[5 specific, actionable networking tactics for finding {JOB_TITLE} roles in {', '.join(LOCATIONS)} — not generic advice.]

---
TARGET_COMPANIES:
[10 companies in Bengaluru and Coimbatore that typically hire Senior Project Managers, with a one-line reason why each is a good fit.]
"""

    console.print("[cyan]Generating networking kit with Claude...[/cyan]\n")

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text

        # Split and display each section
        sections = result.split("---")
        section_styles = {
            "MESSAGE_1": ("LinkedIn Connection Request", "cyan"),
            "MESSAGE_2": ("Cold Outreach to CTO/VP", "blue"),
            "MESSAGE_3": ("Recruiter Outreach", "magenta"),
            "MESSAGE_4": ("Referral Request", "green"),
            "MESSAGE_5": ("Follow-Up (7 days)", "yellow"),
            "MESSAGE_6": ("Thank You After Call", "white"),
            "LINKEDIN_HEADLINE": ("LinkedIn Headline", "bold cyan"),
            "LINKEDIN_ABOUT": ("LinkedIn About Section", "bold blue"),
            "NETWORKING_STRATEGY": ("Networking Strategy", "bold green"),
            "TARGET_COMPANIES": ("Target Companies", "bold magenta"),
        }

        for section in sections:
            section = section.strip()
            if not section:
                continue
            matched = False
            for key, (title, color) in section_styles.items():
                if key in section:
                    content = section.split(":", 1)[-1].strip() if ":" in section else section
                    console.print(Panel(content, title=f"[{color}]{title}[/{color}]", border_style=color))
                    console.print()
                    matched = True
                    break
            if not matched:
                console.print(Panel(section, border_style="white"))
                console.print()

        # Save to file
        out_file = f"networking_kit_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"NETWORKING KIT — {YOUR_NAME} | {JOB_TITLE}\n")
            f.write(f"Locations: {', '.join(LOCATIONS)} | Generated: {datetime.now().strftime('%d %b %Y %H:%M')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(result)

        console.print(f"[green]✓ Full networking kit saved to:[/green] {out_file}")
        console.print("[dim]Tip: Copy each message into LinkedIn — personalize the company/name before sending.[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    run_networking_agent()
