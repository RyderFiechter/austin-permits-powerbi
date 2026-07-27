# Build Guide — Austin Permits in Power BI Desktop

Exact, click-by-click steps. Follow top to bottom; it takes ~2–4 focused hours the first time.
Everything is validated against the **real** dataset column names.

---

## Part 0 — Install Power BI Desktop (Windows, free)

1. Open the **Microsoft Store** → search **“Power BI Desktop”** → **Get / Install**.
   (Alternative: download from `https://www.microsoft.com/en-us/download/details.aspx?id=58494`.)
2. Launch it. Sign-in is optional for building; you can skip it. A free account is only needed if
   you later *publish* to the Power BI Service (not required for a portfolio `.pbix` file).
3. When it opens, close the splash screen — you'll land on **Report view**.

> Power BI Desktop is Windows-only. That's fine — you're on Windows 11.

---

## Part A — Get the data

You have two clean options. **Option 1 (Web/API connector) is recommended** — it makes your
Applied Steps show a real, filtered API pull, which is stronger portfolio evidence.

### Option 1 — Web connector with a server-side filter (recommended)
1. **Home → Get data → Web**.
2. Choose **Basic** and paste this URL (the `$where` filter keeps you from downloading all 2.36M rows):
   ```
   https://data.austintexas.gov/resource/3syk-w9eu.csv?$select=issue_date,applieddate,permit_type_desc,permit_class_mapped,permit_class,work_class,status_current,total_job_valuation,housing_units,number_of_floors,council_district,original_zip,latitude,longitude,contractor_company_name,fiscal_year_issued,calendar_year_issued&$where=fiscal_year_issued >= 2020&$limit=500000
   ```
3. **OK** → on the preview, click **Transform Data** (not Load) to open Power Query Editor.

### Option 2 — Load the CSV in this repo
1. **Home → Get data → Text/CSV** → pick `data/permits_raw.csv` (the raw pull) → **Transform Data**.
   *(Use `permits_raw.csv`, the raw file — the cleaning below is the point. `permits_clean.csv` is
   only a checkpoint to compare your result against.)*

> **Field-name note:** the API returns snake_case names (`total_job_valuation`). If you instead
> used the website's **Export → CSV**, you'd see display names (`Total Job Valuation`). Same
> columns. The table below maps them so nothing is ambiguous.

| Guide/display name | API column name |
|---|---|
| Issue Date | `issue_date` |
| Applied Date | `applieddate` |
| Permit Type (Desc) | `permit_type_desc` |
| Property Class (Permit Class Mapped) | `permit_class_mapped` |
| Permit Class | `permit_class` |
| Work Class | `work_class` |
| Status Current | `status_current` |
| Total Job Valuation | `total_job_valuation` |
| Housing Units | `housing_units` |
| Number Of Floors | `number_of_floors` |
| Council District | `council_district` |
| Original Zip | `original_zip` |
| Latitude / Longitude | `latitude` / `longitude` |
| Contractor Company Name | `contractor_company_name` |
| Fiscal Year Issued | `fiscal_year_issued` |
| Calendar Year Issued | `calendar_year_issued` |

---

## Part B — Power Query cleaning (do these in order)

You're in the **Power Query Editor** (Transform Data). Each step below becomes one entry in the
**Applied Steps** pane on the right — screenshot that pane at the end; it's portfolio evidence.

1. **Filter early for performance.** Click the **Fiscal Year Issued** column dropdown →
   **Number Filters → Greater Than Or Equal To → 2020**. (If you used Option 1, the API already
   filtered this — do it anyway so the step is explicit, or skip and note it.)

2. **Keep only needed columns.** **Home → Choose Columns** → keep exactly the 17 in the table
   above; uncheck everything else (applicant/phone/address, computed-region, valuation-breakdown
   columns, etc.).

3. **Set data types.** Click each column's type icon (left of the header):
   - `issue_date`, `applieddate` → **Date** (drops the time portion of the ISO timestamp).
   - `total_job_valuation` → **Decimal Number**; `housing_units`, `number_of_floors`,
     `fiscal_year_issued`, `calendar_year_issued` → **Whole Number**.

4. **Council District → text category, null → Unknown.** (~30K rows have no district.)
   - Change `council_district` type to **Text** (it's a category 1–10, not a quantity).
   - Replace the nulls. The Replace Values dialog can't type `null` in the UI, so use one of these:
     - **Easiest — Conditional Column:** **Add Column → Conditional Column**, name it
       `Council District`, rule *If `council_district` equals `null` Then `"Unknown"` Else* →
       *(pick “Select a column”)* `council_district`. Then delete the original column.
     - **Or edit the formula bar:** select the column → **Transform → Replace Values** (put anything
       in the boxes), then in the formula bar change the step to
       `= Table.ReplaceValue(#"PrevStep", null, "Unknown", Replacer.ReplaceValue, {"council_district"})`.

5. **Handle missing valuations.** Leave `total_job_valuation` nulls **as null** (so averages ignore
   them). Add a flag: **Add Column → Conditional Column** → name `Has Valuation`,
   *If* `total_job_valuation` **> 0** then `"Yes"` else `"No"`.

6. **Deal with outliers.** Valuations run $0 → ~$8.1B (data-entry errors), and **half of building
   permits are $0/$1 placeholders**. Two defensible options — **document which you chose**:
   - *Recommended:* keep all rows here, and handle the range **in DAX/visuals** by slicing to
     meaningful dollars (the measures in Part D and the $1k–$200M filter). This keeps counts intact.
   - *Alternative:* add a Power Query filter step keeping `total_job_valuation` between 1 and
     200,000,000. Simpler visuals, but you lose trade-permit rows from counts — so prefer the first.

7. **Standardize contractor text.** Select `contractor_company_name` →
   **Transform → Format → Trim**, then **Format → Clean**, then **Format → Capitalize Each Word**.
   Merges `AUSTIN` / `Austin` duplicates so “top contractor” counts are accurate.

8. **Trim status noise.** Click the `status_current` dropdown → uncheck **VOID**, **Withdrawn**,
   **Cancelled** (or the *Void/Withdrawn/Cancelled* variants present). Removes ~4,500 rows that were
   never real; note the choice in your README.

9. **Rename to friendly names** (double-click each header):
   `permit_type_desc → Permit Type`, `permit_class_mapped → Property Class`,
   `total_job_valuation → Total Job Valuation`, `issue_date → Issue Date`,
   `contractor_company_name → Contractor Company Name`, etc. (match the names the DAX in Part D uses).
   Also rename the query itself (left panel) to **Permits**.

10. **Home → Close & Apply.**

> **Checkpoint:** you should land near **429,170 rows**. Compare against `data/permits_clean.csv`
> in this repo — same cleaning logic, same row count. If yours differs a lot, re-check steps 1 & 8.

**README data-quality note to include:** *Because valuation concentrates on Building Permits (and
half of those are $1 placeholders), dollar analysis is done on Building Permits with valuation
$1k–$200M; the electrical/mechanical/plumbing trades are analyzed by permit count.*

---

## Part C — Data model (star schema)

1. **Create the Date table.** **Modeling → New Table**, paste:
   ```DAX
   Date =
   ADDCOLUMNS (
       CALENDAR ( DATE ( 2019, 10, 1 ), DATE ( 2026, 9, 30 ) ),
       "Year",         YEAR ( [Date] ),
       "Month Number", MONTH ( [Date] ),
       "Month",        FORMAT ( [Date], "MMM" ),
       "Quarter",      "Q" & FORMAT ( [Date], "Q" ),
       "Fiscal Year",  IF ( MONTH ( [Date] ) >= 10, YEAR ( [Date] ) + 1, YEAR ( [Date] ) )
   )
   ```
   *(Austin's fiscal year starts Oct 1, so Oct–Dec roll into the next fiscal year.)*
2. **Sort Month correctly:** select the **Month** column → **Column tools → Sort by column →
   Month Number**.
3. **Mark as date table:** select the Date table → **Table tools → Mark as Date Table** → choose
   `[Date]`.
4. **Relationship:** go to **Model view**, drag **`Permits[Issue Date]` → `Date[Date]`**
   (many-to-one, single cross-filter direction). Confirm the arrow points from Date → Permits.
5. *(Optional enhancement)* split out a **Permit Type** dimension and a **Council District**
   dimension and relate them to Permits. Not required for the measures below.

---

## Part D — DAX measures

Create each as a **Measure** (right-click `Permits` → **New measure**), not a column.
Copy-paste ready:

```DAX
Total Permits = COUNTROWS ( Permits )

Total Valuation = SUM ( Permits[Total Job Valuation] )

Building Permits =
CALCULATE ( [Total Permits], Permits[Permit Type] = "Building Permit" )

-- Dollar analysis on meaningful valuations only (drops $0/$1 placeholders + $8.1B outliers)
Building Valuation =
CALCULATE (
    [Total Valuation],
    Permits[Permit Type] = "Building Permit",
    Permits[Total Job Valuation] >= 1000,
    Permits[Total Job Valuation] <= 200000000
)

Avg Project Value =
AVERAGEX (
    FILTER ( Permits, Permits[Total Job Valuation] > 0 ),
    Permits[Total Job Valuation]
)

Residential Valuation =
CALCULATE ( [Building Valuation], Permits[Property Class] = "Residential" )

Commercial Valuation =
CALCULATE ( [Building Valuation], Permits[Property Class] = "Commercial" )

Building Valuation LY =
CALCULATE ( [Building Valuation], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )

YoY Valuation % =
DIVIDE ( [Building Valuation] - [Building Valuation LY], [Building Valuation LY] )

Building Valuation YTD = TOTALYTD ( [Building Valuation], 'Date'[Date] )

% of Total Valuation =
DIVIDE (
    [Building Valuation],
    CALCULATE ( [Building Valuation], ALL ( Permits[Council District] ) )
)

District Rank by Valuation =
RANKX ( ALL ( Permits[Council District] ), [Building Valuation], , DESC )

Housing Units Added =
CALCULATE ( SUM ( Permits[Housing Units] ), Permits[Work Class] = "New" )
```

Format `YoY Valuation %` and `% of Total Valuation` as **Percentage**; `Building Valuation` /
`Avg Project Value` as **Currency**.

> **Why `Building Valuation` instead of raw `Total Valuation` in the visuals:** it bakes in the
> data-quality decision (meaningful-dollar building permits only) so every chart is consistent and
> defensible. Keep plain `Total Valuation` around to show you understand the difference.

---

## Part E — Build the visuals (one clean page)

Suggested layout, top to bottom:

- **Top row — KPI cards** (Card visual ×4): `Building Valuation`, `Total Permits`,
  `Avg Project Value`, `YoY Valuation %`.
- **Map** (Filled map or Azure/bubble map): Location = `Council District` (or Lat/Long),
  bubble size / color = `Building Valuation`. Filter the page to `Permit Type = Building Permit`.
- **Line chart:** X = `Date[Month]` (or `Date[Fiscal Year]`), Y = `Building Valuation` with
  `Building Valuation LY` overlaid → shows the trend and the YoY gap.
- **Bar charts (2):** (a) `Total Permits` by `Permit Type`; (b) `Residential Valuation` vs
  `Commercial Valuation`.
- **Matrix:** Rows = `Council District`, Columns = `Date[Fiscal Year]`, Values =
  `Building Valuation` and `District Rank by Valuation`.
- **Slicers:** `Date[Fiscal Year]`, `Property Class`, `Permit Type`.

Design rules: one story per page; title it *“Where is Austin construction growing?”*; put the three
findings (from the README) in a text box or on a second page.

### Screenshots to capture (portfolio evidence)
Save these into `/screenshots` and reference them in the README:
1. Power Query **Applied Steps** pane (proves the documented cleaning process).
2. **Model view** showing the star schema + marked Date table.
3. The finished **dashboard** page.

---

## Part F — Save & finish
1. **File → Save As** → `AustinPermits.pbix` in the repo root.
2. Fill in `/screenshots`, then update the README's findings if any number shifts.
3. *(Optional)* Publish to the Power BI Service and add a “View live” link — needs a free
   Power BI account with a work/school email; not required for the portfolio.

You now have: a documented Power Query cleaning process, a real star schema with a marked Date
table, time-intelligence DAX, and a written insight tied to a business decision — every bullet the
project brief calls “portfolio-strong,” and four PL-300 exam areas exercised end to end.
