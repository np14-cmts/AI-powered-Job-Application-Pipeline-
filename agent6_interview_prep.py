"""
agent6_interview_prep.py — Agent 6: Interview Prep
Generates a complete interview preparation kit tailored to the JD.

Usage:
    python agent6_interview_prep.py
"""

import os
import anthropic
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

JOB_TITLE    = "Senior Project Manager"
COMPANY_NAME = "Target Company"
LOCATION     = "Bengaluru / Coimbatore"
YEARS_EXP    = "20"

RESUME_SUMMARY = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. PMP-certified. Led cross-functional teams of 30+, delivered
projects worth ₹50Cr+ on time and within budget. Expertise in Agile, Scrum,
Waterfall, JIRA, MS Project, stakeholder management, vendor negotiations, risk
mitigation, and C-level executive reporting across Bengaluru and Coimbatore.
"""

JOB_DESCRIPTION = """
We are looking for a Senior Project Manager with 15+ years of experience to lead
large-scale IT and product delivery projects. The ideal candidate will have PMP
certification, deep expertise in Agile and Waterfall methodologies, experience
managing budgets above ₹20Cr, and strong stakeholder communication skills. Must
have handled multi-location teams, vendor management, and C-level reporting.
Proficiency in JIRA, MS Project, and risk management frameworks required.
Preferred locations: Bengaluru or Coimbatore.
"""

# ─── AGENT ───────────────────────────────────────────────────────────────────

def run_interview_prep_agent():
    console.rule("[bold blue]Agent 6 — Interview Prep[/bold blue]")
    console.print(f"Preparing for: [bold]{JOB_TITLE}[/bold] at [bold]{COMPANY_NAME}[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set your ANTHROPIC_KEY in environment or in this script.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = f"""You are a senior interview coach specializing in IT project management roles in India.

Candidate Resume:
{RESUME_SUMMARY.strip()}

Role: {JOB_TITLE} at {COMPANY_NAME}
Experience: {YEARS_EXP} years
Location: {LOCATION}
Job Description:
{JOB_DESCRIPTION.strip()}

Generate a COMPLETE interview preparation kit:

---
TECHNICAL_QUESTIONS:
Q1: [Question about Agile/Scrum/Waterfall methodology]
WHAT_THEY_ASSESS: [what the interviewer is really testing]
IDEAL_ANSWER_STRUCTURE: [how to frame your answer with a specific example from {YEARS_EXP} years of experience]

Q2: [Question about budget and cost management]
WHAT_THEY_ASSESS:
IDEAL_ANSWER_STRUCTURE:

Q3: [Question about risk management]
WHAT_THEY_ASSESS:
IDEAL_ANSWER_STRUCTURE:

Q4: [Question about JIRA/MS Project and tools]
WHAT_THEY_ASSESS:
IDEAL_ANSWER_STRUCTURE:

---
BEHAVIORAL_QUESTIONS:
B1: [Classic behavioral question for senior PM]
STAR_HINTS: [Situation, Task, Action, Result hints specific to this role]

B2: [Question about handling a failing project]
STAR_HINTS:

B3: [Question about managing difficult stakeholders]
STAR_HINTS:

---
LEADERSHIP_QUESTIONS:
L1: [Question about leading large cross-functional teams]
L2: [Question about vendor management]
L3: [Question about C-level communication]

---
CASE_STUDY:
[A realistic PM case study scenario the interviewer might present, followed by a step-by-step approach to answer it]

---
SALARY_NEGOTIATION:
[Script for negotiating salary for a {JOB_TITLE} targeting {YEARS_EXP} years of experience in India. Include: when to bring it up, what to say, how to counter a low offer, how to handle "what's your current CTC" question]

---
QUESTIONS_TO_ASK:
[7 smart questions to ask the interviewer — mix of role-specific, team, culture, and growth questions. Avoid questions about salary or leave in the first round.]

---
RED_FLAGS_TO_AVOID:
[5 common mistakes senior PM candidates make in interviews and how to avoid them]

---
30_60_90_DAY_PLAN:
[A 30-60-90 day plan to present if asked "what will you do in your first 90 days?" — specific to {JOB_TITLE} role]
"""

    console.print("[cyan]Generating interview prep kit with Claude...[/cyan]\n")

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text

        # Display sections
        sections = result.split("---")
        section_map = {
            "TECHNICAL_QUESTIONS":  ("Technical Questions",       "cyan"),
            "BEHAVIORAL_QUESTIONS": ("Behavioral Questions",      "yellow"),
            "LEADERSHIP_QUESTIONS": ("Leadership Questions",      "blue"),
            "CASE_STUDY":           ("Case Study Scenario",       "magenta"),
            "SALARY_NEGOTIATION":   ("Salary Negotiation Script", "green"),
            "QUESTIONS_TO_ASK":     ("Questions to Ask Them",     "white"),
            "RED_FLAGS_TO_AVOID":   ("Red Flags to Avoid",        "red"),
            "30_60_90_DAY_PLAN":    ("30-60-90 Day Plan",         "bold cyan"),
        }

        for section in sections:
            section = section.strip()
            if not section:
                continue
            matched = False
            for key, (title, color) in section_map.items():
                if key in section:
                    content = "\n".join(
                        line for line in section.split("\n")
                        if key not in line
                    ).strip()
                    console.print(Panel(content, title=f"[{color}]{title}[/{color}]", border_style=color))
                    console.print()
                    matched = True
                    break
            if not matched and len(section) > 10:
                console.print(Panel(section, border_style="white"))
                console.print()

        # Save to file
        out_file = f"interview_prep_{COMPANY_NAME.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"INTERVIEW PREP KIT\n")
            f.write(f"Role: {JOB_TITLE} | Company: {COMPANY_NAME}\n")
            f.write(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(result)

        console.print(f"[green]✓ Interview prep kit saved to:[/green] {out_file}")
        console.print("[dim]Tip: Practice each answer out loud. Time yourself — aim for 2–3 minutes per answer.[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    run_interview_prep_agent()
