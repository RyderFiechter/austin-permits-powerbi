# Resume & Interview Kit — Austin Permits project

## Project title (pick one)
- **Austin Construction Market Analysis — Power BI**
- **Where Is Austin Building? A Contractor-Market Opportunity Dashboard (Power BI)**

## Resume bullets

Use 2–3. They're written to pair with your existing ETL / market-analysis project and your SDR
account-targeting work, so the whole resume tells one story: *finding where demand forms.*

**Tight (3 bullets):**
- Built an end-to-end Power BI market-analysis dashboard on **429K City of Austin construction
  permits (FY2020–2026)** — Power Query ETL, a star-schema data model with a marked fiscal Date
  table, and time-intelligence DAX (YoY, YTD, RANKX) — to identify the strongest districts and
  segments for a company selling to contractors.
- Engineered defensible cleaning decisions on genuinely messy public data — **83% null valuations,
  half of building permits filed at $1 placeholders, outliers to $8.1B** — documenting each choice
  (e.g., scoping dollar analysis to $1k–$200M building permits, which moved the median project value
  from $1 to $170K).
- Turned the model into a decision: identified that construction dollars are **rotating into
  Central/East Austin (Districts 1–4, +104–275% YoY)** even as the citywide market cooled, and
  recommended segmenting outreach — commercial builders for high-value project tooling, the
  electrical/plumbing/mechanical trades (~328K permits) for volume.

**One-line version (for a skills/projects strip):**
- *Austin Permits (Power BI):* 429K-row ETL → star schema → time-intelligence DAX → a district-level
  contractor-market opportunity dashboard with three action-oriented findings.

## Skills this demonstrates (map to job descriptions)
Power BI · Power Query (M) · DAX (CALCULATE, DIVIDE, SAMEPERIODLASTYEAR, TOTALYTD, ALL, RANKX) ·
data modeling / star schema · data cleaning & QA · REST/Socrata API extraction ·
Python (pandas) for validation · business/market analysis · data storytelling.

Also: it exercises **four of the four scored PL-300 areas** (Prepare, Model, Visualize,
+ DAX throughout), so list *“PL-300 Power BI Data Analyst — in progress”* if applicable.

## How to present it
1. Put the **dashboard screenshot** and the **three findings** at the top of the write-up.
2. Link the GitHub repo (README is the centerpiece) and, if you publish, the live Power BI report.
3. In the repo, the `/screenshots` of Applied Steps + model diagram are the proof you did the work.

## Interview talking points

- **"Walk me through the project."** Business question first (where is contractor demand growing),
  then the five stages, then land on the rotation-into-East-Austin finding. 90 seconds.
- **"What was the hardest data problem?"** The valuations: 83% null and half of the non-nulls were
  $1 placeholders. Explain *why* (valuation lives on Building Permits; trades carry none; new-home
  permits get $1 placeholders) and the decision (dollars → building permits $1k–$200M; everything
  else → counts). This is the answer that signals "analyst," not "chart-maker."
- **"Why a Date table / star schema?"** Time-intelligence DAX (YoY, YTD) needs a marked date table;
  a star schema keeps measures clean and filters predictable vs. one flat sheet.
- **"What would you do next?"** Add contractor-level churn (who's active this year vs last),
  geocode to sub-district trade areas, and validate the $1-placeholder theory against building sqft.
- **Domain tie-in (for HCSS-type roles):** you already understand the construction/contractor world;
  this shows you can quantify *where* that world is spending and turn it into a targeting list.

## Honesty guardrails (so you can defend every number)
- FY2026 is **partial** — never quote it as a full-year YoY.
- Dollar figures use the **$1k–$200M building-permit** filter; say so if asked.
- Residential dollars are **understated** (placeholders) — lead residential with counts / housing units.
- All numbers are reproducible from `scripts/final_insights.py` against the cleaned data.
