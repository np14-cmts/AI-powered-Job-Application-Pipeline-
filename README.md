# 🤖 AI-Powered Job Application Pipeline

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Claude](https://img.shields.io/badge/Powered%20by-Claude%20Sonnet-orange?logo=anthropic)
![Playwright](https://img.shields.io/badge/Scraping-Playwright-green?logo=microsoft)
![Portals](https://img.shields.io/badge/Portals-LinkedIn%20%7C%20Naukri-0A66C2)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> An end-to-end AI pipeline that searches LinkedIn & Naukri for **Senior Project Manager** roles in **Bengaluru / Coimbatore**, runs Claude-powered fitment analysis against each JD, rewrites your resume, generates networking messages, and preps you for interviews — all automatically.

---

## 📋 Pipeline Overview

```
Your Resume + Job Title + Location
            ↓
    ┌───────────────────┐
    │  AI Agent Hub     │
    └───────────────────┘
            ↓
┌─────────────────────────────────────────────────────┐
│  Agent 2: Fitment & Gap Analysis                    │
│  → Scores resume vs JD, lists matches & gaps        │
├─────────────────────────────────────────────────────┤
│  Agent 3: Resume Rewrite                            │
│  → ATS-optimized resume + cover letter              │
├─────────────────────────────────────────────────────┤
│  Agent 4: Auto-Apply Strategy                       │
│  → Best portals, keywords, opens browser tabs       │
├─────────────────────────────────────────────────────┤
│  Agent 5: Networking Agent                          │
│  → LinkedIn messages, recruiter outreach, targets   │
├─────────────────────────────────────────────────────┤
│  Agent 6: Interview Prep                            │
│  → Questions, STAR answers, case study, 90-day plan │
└─────────────────────────────────────────────────────┘
            ↓
  📊 Excel Report + 🌐 Browser Tabs + 📄 Text Files
```

---

## 📁 File Structure

```
AI-powered-Job-Application-Pipeline/
│
├── job_pipeline.py          # 🚀 Main pipeline — scrapes + analyzes all jobs
├── agent2_fitment.py        # 🎯 Fitment & gap analysis against one JD
├── agent3_resume_rewrite.py # 📝 Resume rewrite + cover letter
├── agent4_auto_apply.py     # 🔗 Apply strategy + opens portals in browser
├── agent5_networking.py     # 🤝 LinkedIn messages + networking kit
├── agent6_interview_prep.py # 🎤 Full interview prep kit
├── config.py                # ⚙️  Central configuration (edit this first)
├── requirements.txt         # 📦 Python dependencies
├── .gitignore               # 🚫 Files to exclude from git
└── README.md                # 📖 This file
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/np14-cmts/AI-powered-Job-Application-Pipeline-.git
cd AI-powered-Job-Application-Pipeline-
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Set your Anthropic API key
Get your free key from [console.anthropic.com](https://console.anthropic.com)

**Mac/Linux:**
```bash
export ANTHROPIC_KEY=sk-ant-your-key-here
```
**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_KEY="sk-ant-your-key-here"
```
**Or** open `config.py` and paste it directly.

### 4. Edit your profile in `config.py`
```python
RESUME     = "Your resume summary here..."
JOB_TITLE  = "Senior Project Manager"
LOCATIONS  = ["Bengaluru", "Coimbatore"]
YEARS_EXP  = "20"
```

### 5. Run the full pipeline
```bash
python job_pipeline.py
```

Or run individual agents:
```bash
python agent2_fitment.py        # Analyze one JD
python agent3_resume_rewrite.py # Rewrite resume
python agent4_auto_apply.py     # Open job portals
python agent5_networking.py     # Generate outreach messages
python agent6_interview_prep.py # Interview prep kit
```

---

## 📊 Output Files

| File | Description |
|------|-------------|
| `job_fitment_report_YYYYMMDD.xlsx` | Color-coded Excel with all jobs ranked by fit % |
| `fitment_report.txt` | Detailed fitment analysis for one JD |
| `resume_Senior_Project_Manager_YYYYMMDD.txt` | Tailored resume |
| `cover_letter_Company_YYYYMMDD.txt` | Matching cover letter |
| `apply_strategy_YYYYMMDD.txt` | Full application strategy |
| `networking_kit_YYYYMMDD.txt` | All LinkedIn messages + target companies |
| `interview_prep_Company_YYYYMMDD.txt` | Complete interview prep kit |

### Excel Color Coding
| Color | Meaning |
|-------|---------|
| 🟢 Green | Strong match ≥ 85% |
| 🟡 Yellow | Good match 65–84% |
| 🔴 Red | Weak match < 65% |

---

## ⚙️ Configuration Options (`config.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_KEY` | env var | Your Claude API key |
| `RESUME` | Senior PM profile | Paste your resume summary |
| `JOB_TITLE` | Senior Project Manager | Target role |
| `LOCATIONS` | Bengaluru, Coimbatore | Cities to search |
| `MAX_JOBS` | 15 | Total jobs to scrape |
| `TOP_N_OPEN` | 5 | Top matches to open in browser |
| `MIN_FIT_PCT` | 50 | Minimum fit % to include in report |
| `SEARCH_LINKEDIN` | True | Enable LinkedIn scraping |
| `SEARCH_NAUKRI` | True | Enable Naukri scraping |

---

## 💰 API Cost

Each full pipeline run makes ~15–25 Claude API calls.
- Estimated cost: **₹4–10 per full run**
- Individual agents: **₹0.50–2 per run**

---

## ⚠️ Notes

- **LinkedIn** may ask you to log in — do so manually if prompted; subsequent runs will reuse the session
- **Naukri** works without login
- Auto-submitting applications requires additional Playwright automation (not included by default — to avoid violating portal ToS)
- Generated outreach messages should be **personalized** before sending on LinkedIn

---

## 🛠️ Built With

- [Anthropic Claude](https://anthropic.com) — AI fitment, rewriting, prep
- [Playwright](https://playwright.dev/python/) — Browser automation & scraping
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel report generation
- [Rich](https://rich.readthedocs.io/) — Beautiful terminal output

---

## 📄 License

MIT License — use freely, attribution appreciated.
