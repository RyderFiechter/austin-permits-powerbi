# Data

The full datasets are **not committed** (they're large and fully regenerable). This folder ships
a small sample so you can see the schema:

- **`permits_clean_sample.csv`** — first 5,000 rows of the cleaned dataset (committed).

## Regenerate the full data

```bash
# 1. Pull the raw FY2020+ data from the City of Austin Socrata API (~86 MB, 433,669 rows)
#    (or use Power BI's Web connector — see ../docs/BUILD_GUIDE.md, Part A)
curl -s "https://data.austintexas.gov/resource/3syk-w9eu.csv?\$select=issue_date,applieddate,permit_type_desc,permit_class_mapped,permit_class,work_class,status_current,total_job_valuation,housing_units,number_of_floors,council_district,original_zip,latitude,longitude,contractor_company_name,fiscal_year_issued,calendar_year_issued&\$where=fiscal_year_issued%20%3E=%202020&\$limit=500000" -o data/permits_raw.csv

# 2. Clean it (mirrors the Power Query steps) -> data/permits_clean.csv + profiling
python scripts/profile_and_clean.py

# 3. Compute the findings cited in the top-level README
python scripts/final_insights.py
```

Source: [Issued Construction Permits — City of Austin Open Data](https://data.austintexas.gov/dataset/Issued-Construction-Permits/3syk-w9eu)
(dataset ID `3syk-w9eu`).
