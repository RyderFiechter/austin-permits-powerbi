"""
Austin Construction Permits — profile the raw FY2020+ pull, apply the same
cleaning logic the Power BI Power Query steps describe, and emit:
  1. a cleaned CSV for Power BI import (data/permits_clean.csv)
  2. a profiling / insights report printed to stdout (captured to docs/)

Field names here are the raw Socrata API (snake_case). The guide's "friendly"
names are the Export->CSV display names; both refer to the same columns.
"""
import pandas as pd
import numpy as np
import io, sys

RAW = "data/permits_raw.csv"

# ---- load -------------------------------------------------------------
df = pd.read_csv(RAW, low_memory=False)
print("RAW SHAPE:", df.shape)
print("COLUMNS:", list(df.columns))
print()

# ---- basic profiling before cleaning ----------------------------------
print("=== NULL COUNTS (raw) ===")
print(df.isna().sum().to_string())
print()

# valuation nullness
tv = "total_job_valuation"
print(f"total_job_valuation: null={df[tv].isna().mean():.1%}, "
      f"min={df[tv].min()}, max={df[tv].max()}")
print()

# permit type distribution
print("=== permit_type_desc counts ===")
print(df["permit_type_desc"].value_counts(dropna=False).to_string())
print()

# ---- CLEANING (mirrors Power Query Part B) ----------------------------
# 3. dates
df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce").dt.normalize()
df["applieddate"] = pd.to_datetime(df["applieddate"], errors="coerce").dt.normalize()

# numeric types
for c in ["total_job_valuation", "housing_units", "number_of_floors",
          "fiscal_year_issued", "calendar_year_issued"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# 4. council district -> text category, null -> Unknown
df["council_district"] = df["council_district"].apply(
    lambda x: "Unknown" if pd.isna(x) else str(int(x)) if float(x).is_integer() else str(x)
)

# 5. Has Valuation conditional column (blanks left blank)
df["has_valuation"] = np.where(df[tv] > 0, "Yes", "No")

# 7. standardize contractor text: trim, clean, capitalize each word
def clean_txt(x):
    if pd.isna(x):
        return x
    s = " ".join(str(x).split())          # trim + collapse internal whitespace (Clean)
    return s.title()                       # Capitalize Each Word
df["contractor_company_name"] = df["contractor_company_name"].apply(clean_txt)

# 8. trim status noise
before = len(df)
bad_status = ["Void", "Withdrawn", "Cancelled"]
df = df[~df["status_current"].isin(bad_status)].copy()
print(f"Status filter removed {before-len(df):,} rows "
      f"(Void/Withdrawn/Cancelled). Remaining: {len(df):,}")
print()

# 9. friendly renames (to match the guide's model/DAX field names)
df = df.rename(columns={
    "permit_type_desc": "Permit Type",
    "permit_class_mapped": "Property Class",
    "permit_class": "Permit Class",
    "work_class": "Work Class",
    "status_current": "Status Current",
    "total_job_valuation": "Total Job Valuation",
    "housing_units": "Housing Units",
    "number_of_floors": "Number Of Floors",
    "council_district": "Council District",
    "original_zip": "Original Zip",
    "issue_date": "Issue Date",
    "applieddate": "Applied Date",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "contractor_company_name": "Contractor Company Name",
    "fiscal_year_issued": "Fiscal Year Issued",
    "calendar_year_issued": "Calendar Year Issued",
    "has_valuation": "Has Valuation",
})

# ---- write cleaned file for Power BI ----------------------------------
OUT = "data/permits_clean.csv"
df.to_csv(OUT, index=False)
print(f"Wrote {OUT}: {df.shape[0]:,} rows x {df.shape[1]} cols")
print()

# ---- INSIGHTS ---------------------------------------------------------
print("#" * 60)
print("INSIGHTS")
print("#" * 60)

# valuation concentration by permit type (why guide says dollars=Building)
print("\n=== Share of total valuation by Permit Type ===")
vt = df.groupby("Permit Type")["Total Job Valuation"].sum().sort_values(ascending=False)
print((vt / vt.sum()).map(lambda x: f"{x:.1%}").to_string())

# Property class split
print("\n=== Valuation by Property Class (Building permits only) ===")
bld = df[df["Permit Type"] == "Building Permit"]
print(bld.groupby("Property Class")["Total Job Valuation"].sum()
      .sort_values(ascending=False).map(lambda x: f"${x:,.0f}").to_string())

# YoY valuation by fiscal year (Building permits, capped outliers 1..200M)
print("\n=== Building-permit valuation by Fiscal Year (outliers capped 1..200M) ===")
capped = bld[(bld["Total Job Valuation"] >= 1) & (bld["Total Job Valuation"] <= 200_000_000)]
fy = capped.groupby("Fiscal Year Issued")["Total Job Valuation"].sum()
cnt = capped.groupby("Fiscal Year Issued")["Total Job Valuation"].size()
tbl = pd.DataFrame({"valuation": fy, "permits": cnt})
tbl["yoy_%"] = tbl["valuation"].pct_change().map(lambda x: f"{x:+.1%}" if pd.notna(x) else "")
print(tbl.assign(valuation=lambda d: d["valuation"].map(lambda x: f"${x:,.0f}")).to_string())

# District ranking by valuation (Building, capped), latest full fiscal year vs prior
print("\n=== Top districts by Building valuation, FY2024 vs FY2023 (capped) ===")
def dist_val(year):
    sub = capped[capped["Fiscal Year Issued"] == year]
    return sub.groupby("Council District")["Total Job Valuation"].sum()
d24, d23 = dist_val(2024), dist_val(2023)
comp = pd.DataFrame({"FY2023": d23, "FY2024": d24}).fillna(0)
comp["YoY_%"] = ((comp["FY2024"] - comp["FY2023"]) / comp["FY2023"].replace(0, np.nan))
comp = comp.sort_values("FY2024", ascending=False)
print(comp.assign(
    FY2023=lambda d: d["FY2023"].map(lambda x: f"${x/1e6:,.0f}M"),
    FY2024=lambda d: d["FY2024"].map(lambda x: f"${x/1e6:,.0f}M"),
    YoY_=lambda d: d["YoY_%"].map(lambda x: f"{x:+.1%}" if pd.notna(x) else "n/a"),
).drop(columns="YoY_%").rename(columns={"YoY_": "YoY_%"}).to_string())

# Fastest-growing districts (residential building valuation)
print("\n=== Residential Building valuation by district: FY2024 vs FY2023 ===")
res = capped[capped["Property Class"] == "Residential"]
def rdist(year):
    return res[res["Fiscal Year Issued"] == year].groupby("Council District")["Total Job Valuation"].sum()
r24, r23 = rdist(2024), rdist(2023)
rcomp = pd.DataFrame({"FY2023": r23, "FY2024": r24}).fillna(0)
rcomp["YoY_%"] = ((rcomp["FY2024"] - rcomp["FY2023"]) / rcomp["FY2023"].replace(0, np.nan))
rcomp = rcomp[rcomp.index != "Unknown"].sort_values("YoY_%", ascending=False)
print(rcomp.assign(
    FY2023=lambda d: d["FY2023"].map(lambda x: f"${x/1e6:,.1f}M"),
    FY2024=lambda d: d["FY2024"].map(lambda x: f"${x/1e6:,.1f}M"),
    YoY_=lambda d: d["YoY_%"].map(lambda x: f"{x:+.1%}" if pd.notna(x) else "n/a"),
).drop(columns="YoY_%").rename(columns={"YoY_": "YoY_%"}).to_string())

# Housing units added (new work class) by fiscal year and district
print("\n=== Housing Units Added (Work Class = New) by Fiscal Year ===")
newu = df[df["Work Class"] == "New"]
print(newu.groupby("Fiscal Year Issued")["Housing Units"].sum().map(lambda x: f"{x:,.0f}").to_string())

# Top contractors by building-permit count
print("\n=== Top 10 contractors by permit count ===")
print(df["Contractor Company Name"].value_counts().head(10).to_string())

# Avg project value (nonzero)
nz = df[df["Total Job Valuation"] > 0]["Total Job Valuation"]
print(f"\nAvg project value (nonzero valuations): ${nz.mean():,.0f}")
print(f"Median project value (nonzero): ${nz.median():,.0f}")
print(f"Rows with valuation > 0: {(df['Has Valuation']=='Yes').mean():.1%}")
