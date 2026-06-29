"""
agent2_fitment.py — Agent 2: Fitment & Gap Analysis
Compares your resume against a job description and scores the match.

Usage:
    python agent2_fitment.py
"""

import os
import re
import anthropic
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

RESUME = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. Proven track record of leading cross-functional teams of 30+
members, delivering projects worth ₹50Cr+ on time and within budget. Expertise in
Agile, Scrum, Waterfall, PMP-certified, stakeholder management, risk mitigation,
and vendor negotiations. Managed multi-site projects across Bengaluru and Coimbatore.
Strong in JIRA, MS Project, and C-level executive reporting.
"""

JOB_TITLE = "Senior Project Manager"
LOCATION  = "Bengaluru / Coimbatore"
YEARS_EXP = "20"

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

def run_fitment_agent():
    console.rule("[bold blue]Agent 2 — Fitment & Gap Analysis[/bold blue]")
    console.print(f"Role: [bold]{JOB_TITLE}[/bold] | Location: [bold]{LOCATION}[/bold] | Experience: [bold]{YEARS_EXP} years[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set your ANTHROPIC_KEY in environment or in this script.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = f"""You are an expert resume fitment analyzer for senior-level roles.

Resume:
{RESUME.strip()}

Job Title: {JOB_TITLE}
Location: {LOCATION}
Years of Experience: {YEARS_EXP}
Job Description:
{JOB_DESCRIPTION.strip()}

Provide a detailed fitment analysis in EXACTLY this format:

FIT_SCORE: [number 0-100]

MATCHED_SKILLS:
- skill or strength 1
- skill or strength 2
- skill or strength 3
- skill or strength 4
- skill or strength 5

SKILL_GAPS:
- gap 1 with brief explanation
- gap 2 with brief explanation
- gap 3 with brief explanation

EXPERIENCE_GAPS:
- any experience gap 1
- any experience gap 2

STRENGTHS:
- key differentiator 1
- key differentiator 2
- key differentiator 3

VERDICT:
One clear paragraph with overall suitability, what stands out, and what to fix before applying.

PRIORITY_ACTIONS:
1. action to take immediately
2. action to take before applying
3. action to strengthen profile
"""

    console.print("[cyan]Analyzing fitment with Claude...[/cyan]\n")

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text

        # Parse sections
        fit_score    = (re.search(r"FIT_SCORE:\s*(\d+)", result) or [None, "N/A"])[1]
        matched      = re.findall(r"MATCHED_SKILLS:\n(.*?)(?=\n[A-Z_]+:)", result, re.DOTALL)
        gaps         = re.findall(r"SKILL_GAPS:\n(.*?)(?=\n[A-Z_]+:)", result, re.DOTALL)
        exp_gaps     = re.findall(r"EXPERIENCE_GAPS:\n(.*?)(?=\n[A-Z_]+:)", result, re.DOTALL)
        strengths    = re.findall(r"STRENGTHS:\n(.*?)(?=\n[A-Z_]+:)", result, re.DOTALL)
        verdict      = re.findall(r"VERDICT:\n(.*?)(?=\n[A-Z_]+:|$)", result, re.DOTALL)
        actions      = re.findall(r"PRIORITY_ACTIONS:\n(.*?)$", result, re.DOTALL)

        # Display fit score
        score = int(fit_score) if fit_score.isdigit() else 0
        color = "green" if score >= 85 else "yellow" if score >= 65 else "red"
        label = "Strong Match" if score >= 85 else "Good Match" if score >= 65 else "Weak Match"

        console.print(Panel(
            f"[bold {color}]{score}% — {label}[/bold {color}]",
            title="Overall Fitment Score",
            border_style=color,
            expand=False
        ))
        console.print()

        # Matched skills
        if matched:
            console.print(Panel(matched[0].strip(), title="[green]✓ Matched Skills & Strengths[/green]", border_style="green"))

        # Skill gaps
        if gaps:
            console.print(Panel(gaps[0].strip(), title="[yellow]⚠ Skill Gaps[/yellow]", border_style="yellow"))

        # Experience gaps
        if exp_gaps:
            console.print(Panel(exp_gaps[0].strip(), title="[yellow]⚠ Experience Gaps[/yellow]", border_style="yellow"))

        # Strengths
        if strengths:
            console.print(Panel(strengths[0].strip(), title="[blue]★ Key Differentiators[/blue]", border_style="blue"))

        # Verdict
        if verdict:
            console.print(Panel(verdict[0].strip(), title="[bold]Verdict[/bold]", border_style="white"))

        # Priority actions
        if actions:
            console.print(Panel(actions[0].strip(), title="[cyan]Priority Actions Before Applying[/cyan]", border_style="cyan"))

        # Save to file
        output_file = "fitment_report.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"FITMENT REPORT — {JOB_TITLE}\n")
            f.write(f"Location: {LOCATION} | Experience: {YEARS_EXP} years\n")
            f.write("=" * 60 + "\n\n")
            f.write(result)
        console.print(f"\n[green]✓ Full report saved to:[/green] {output_file}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    run_fitment_agent()
