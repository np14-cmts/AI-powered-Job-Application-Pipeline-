"""
config.py — Edit this file to customize your job search pipeline.
"""

import os

# ── Anthropic API ─────────────────────────────────────────────────────────────
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "YOUR_API_KEY_HERE")

# ── Your Resume ───────────────────────────────────────────────────────────────
RESUME = """
20 years of experience in end-to-end project management across IT, infrastructure,
and product delivery. Proven track record of leading cross-functional teams of 30+
members, delivering projects worth ₹50Cr+ on time and within budget. Expertise in
Agile, Scrum, Waterfall, PMP-certified, stakeholder management, risk mitigation,
and vendor negotiations. Managed multi-site projects across Bengaluru and Coimbatore.
Strong in JIRA, MS Project, and C-level executive reporting.
"""

# ── Search Settings ───────────────────────────────────────────────────────────
JOB_TITLE  = "Senior Project Manager"
LOCATIONS  = ["Bengaluru", "Coimbatore"]
MAX_JOBS   = 15       # Total jobs to scrape across both portals
TOP_N_OPEN = 5        # Top N matches to auto-open in browser
MIN_FIT_PCT = 50      # Skip jobs below this fitment % threshold

# ── Portals to search ─────────────────────────────────────────────────────────
SEARCH_LINKEDIN = True
SEARCH_NAUKRI   = True
