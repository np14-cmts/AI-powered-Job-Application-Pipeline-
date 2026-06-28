# AI Job Pipeline — Setup Guide

## Prerequisites
- Python 3.9+
- Anthropic API key (get from https://console.anthropic.com)

## 1. Install dependencies

```bash
pip install anthropic playwright openpyxl requests beautifulsoup4 rich
playwright install chromium
```

## 2. Set your Anthropic API key

### Windows (Command Prompt)
```cmd
set ANTHROPIC_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

### Windows (PowerShell)
```powershell
$env:ANTHROPIC_KEY="sk-ant-xxxxxxxxxxxxxxxx"
```

### Mac / Linux
```bash
export ANTHROPIC_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

Alternatively, open `job_pipeline.py` and replace `YOUR_API_KEY_HERE` directly.

## 3. Run the pipeline

```bash
python job_pipeline.py
```

## What it does

1. Searches LinkedIn and Naukri for "Senior Project Manager" jobs in Bengaluru and Coimbatore
2. Fetches each job description automatically
3. Sends resume + JD to Claude for fitment scoring
4. Filters jobs below 50% match
5. Exports a color-coded Excel report ranked by fit %
6. Opens top 5 matches (≥75% fit) in your browser

## Output

- `job_fitment_report_YYYYMMDD_HHMM.xlsx` — ranked Excel report
  - Green rows = Strong match (≥85%)
  - Yellow rows = Good match (65–84%)
  - Red rows = Weak match (<65%)
- Top matches auto-opened in browser

## Customizing

Edit the CONFIG section at the top of `job_pipeline.py`:

| Variable      | Default                   | Description                        |
|---------------|---------------------------|------------------------------------|
| RESUME        | (your resume)             | Paste your full resume here        |
| JOB_TITLE     | Senior Project Manager    | The role you're targeting          |
| LOCATIONS     | Bengaluru, Coimbatore     | Cities to search in                |
| MAX_JOBS      | 15                        | Max jobs to scrape                 |
| TOP_N_OPEN    | 5                         | How many to auto-open in browser   |
| MIN_FIT_PCT   | 50                        | Skip jobs below this fit %         |

## Notes

- LinkedIn may require login for some listings — run once, if prompted log in manually in the browser window
- Naukri works without login
- Each run costs ~15–20 Claude API calls (very low cost, ~$0.05–0.10 per run)
- Add a delay between runs if you hit rate limits
