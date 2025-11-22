# GigRadar Support Engineer Technical Test

## Deliverables

### 1. Google Spreadsheet
🔗 [https://docs.google.com/spreadsheets/d/18LYlxJJuJr7Sr_MCxJZ9wckD7X0bpae7ew2DYcBNPaA/edit?usp=sharing]
---

### 2. Zapier Automation
- Using spreadsheet update row trigger
- Sends Telegram message with: Agency Name, Freelancer Name, Upwork Link, Status
- Downloaded into json -> exported-zap-workflow.json
---

### 3. Analysis Results
- The analysis made in anaylsis.ipynb
#### Top 3 Variables Impacting Earnings:
| Rank | Variable | Feature Importance | Correlation |
|------|----------|-------------------|-------------|
| 1 | **Total Hourly Jobs** | 24.9% | +0.0252 |
| 2 | **Avg Feedback Score** | 20.4% | -0.0573 |
| 3 | **Avg Deadlines Score** | 16.5% | -0.0232 |
---

#### Top 5 Highest-Earning Freelancers:
| Rank | Freelancer | Company | Service | Skill 1 | Skill 2 | Earnings |
|------|------------|---------|---------|---------|---------|----------|
| 1 | Kiran T. | SmartData Inc Agency | Emerging Tech | Emerging Tech Services – Emerging Tech Consultation | Emerging Tech Services – Research & Development | $60,680,280 |
| 2 | Andrew M. | MobiDev | AR/VR Development | Databases – SQLite | Databases – PostgreSQL | $29,826,859 |
| 3 | Denis D. | MobiDev | Emerging Tech | N/A | N/A | $29,797,255 |
| 4 | Nikolay S. | MobiDev | Emerging Tech | N/A | N/A | $29,797,255 |
| 5 | Peter C. | MobiDev | Emerging Tech | N/A | N/A | $29,740,262 |
---

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in values
3. Run: `python ingest_data.py`