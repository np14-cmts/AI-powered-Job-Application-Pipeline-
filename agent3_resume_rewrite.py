"""
agent3_resume_rewrite.py — Agent 3: Resume Rewrite
Rewrites your resume tailored to the target job description (ATS-optimized).

Usage:
    python agent3_resume_rewrite.py
"""

import os
import anthropic
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

CANDIDATE_NAME    = "Your Full Name"
CANDIDATE_EMAIL   = "your.email@example.com"
CANDIDATE_PHONE   = "+91-XXXXXXXXXX"
CANDIDATE_LINKEDIN = "linkedin.com/in/yourprofile"

RESUME = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. Proven track record of leading cross-functional teams of 30+
members, delivering projects worth ₹50Cr+ on time and within budget. Expertise in
Agile, Scrum, Waterfall, PMP-certified, stakeholder management, risk mitigation,
and vendor negotiations. Managed multi-site projects across Bengaluru and Coimbatore.
Strong in JIRA, MS Project, and C-level executive reporting.
"""

JOB_TITLE    = "Senior Project Manager"
LOCATION     = "Bengaluru / Coimbatore"
YEARS_EXP    = "20"
COMPANY_NAME = "Target Company"

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

def run_resume_rewrite_agent():
    console.rule("[bold blue]Agent 3 — Resume Rewrite[/bold blue]")
    console.print(f"Tailoring resume for: [bold]{JOB_TITLE}[/bold] at [bold]{COMPANY_NAME}[/bold]\n")

    if ANTHROPIC_KEY == "YOUR_API_KEY_HERE":
        console.print("[red]ERROR:[/red] Set your ANTHROPIC_KEY in environment or in this script.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = f"""You are an expert resume writer specializing in senior-level IT and project management roles in India.

Original Resume Summary:
{RESUME.strip()}

Target Role: {JOB_TITLE}
Target Company: {COMPANY_NAME}
Location: {LOCATION}
Years of Experience: {YEARS_EXP}

Job Description:
{JOB_DESCRIPTION.strip()}

Rewrite a complete, ATS-optimized resume with these EXACT sections:

PROFESSIONAL_SUMMARY:
[3 powerful sentences. Open with years of experience and domain. Mention PMP, key tools, and biggest impact metric.]

CORE_COMPETENCIES:
[12 skills as comma-separated keywords directly from the JD — for ATS scanning]

KEY_ACHIEVEMENTS:
[6 bullet points. Each must: start with an action verb, include a metric/number, and directly map to a JD requirement.]

TECHNICAL_SKILLS:
[Methodologies: | Tools: | Certifications: | Reporting:]

PROFESSIONAL_EXPERIENCE:
[Most recent role first. 2 roles with title, company, location, dates, and 4 bullet points each.]

EDUCATION:
[Degree, Institution, Year]

CERTIFICATIONS:
[PMP and any others]

Make every line keyword-rich for ATS. Use strong action verbs. All metrics must be realistic and consistent with {YEARS_EXP} years of experience.
"""

    console.print("[cyan]Generating tailored resume with Claude...[/cyan]\n")

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text

        # Display in terminal
        console.print(Panel(result, title=f"[bold green]Tailored Resume — {JOB_TITLE}[/bold green]", border_style="green"))

        # Save as plain text
        txt_file = f"resume_{JOB_TITLE.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(f"{CANDIDATE_NAME}\n")
            f.write(f"{CANDIDATE_EMAIL} | {CANDIDATE_PHONE} | {CANDIDATE_LINKEDIN}\n")
            f.write(f"{LOCATION}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"TARGET ROLE: {JOB_TITLE} at {COMPANY_NAME}\n\n")
            f.write("=" * 70 + "\n\n")
            f.write(result)

        console.print(f"\n[green]✓ Resume saved to:[/green] {txt_file}")
        console.print("[dim]Tip: Copy this into a Word doc or use a resume builder to format it professionally.[/dim]")

        # Also generate a cover letter
        console.print("\n[cyan]Generating matching cover letter...[/cyan]")
        cover_prompt = f"""Write a professional cover letter for {CANDIDATE_NAME} applying for {JOB_TITLE} at {COMPANY_NAME}.
Use this resume: {RESUME.strip()}
And this JD: {JOB_DESCRIPTION.strip()}
Keep it to 3 paragraphs: opening hook, 2-3 key achievements matching the JD, closing with call to action.
Address it to 'Dear Hiring Manager'. Sign off as {CANDIDATE_NAME}."""

        cover_msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": cover_prompt}]
        )
        cover = cover_msg.content[0].text

        cover_file = f"cover_letter_{COMPANY_NAME.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(cover_file, "w", encoding="utf-8") as f:
            f.write(cover)

        console.print(Panel(cover, title="[bold blue]Cover Letter[/bold blue]", border_style="blue"))
        console.print(f"[green]✓ Cover letter saved to:[/green] {cover_file}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    run_resume_rewrite_agent()
