"""Final, defensible insight numbers for the README/narrative.
Decisions documented:
  - Dollar analysis uses Total Job Valuation between $1,000 and $200,000,000.
    (>= $1,000 drops the ~47k building permits filed with $0/$1 placeholders;
     <= $200M drops 99 data-entry outliers up to $8.1B.)
  - Counts use all issued permits (dollars aren't meaningful on trade permits).
  - YoY headlines compare COMPLETE fiscal years only. FY2026 is partial
    (data ends 2026-07-26), so it is shown but flagged, never used as a YoY endpoint.
"""
import pandas as pd, numpy as np

df = pd.read_csv("data/permits_clean.csv", low_memory=False)
df["Issue Date"] = pd.to_datetime(df["Issue Date"])
V = "Total Job Valuation"

bld = df[df["Permit Type"] == "Building Permit"].copy()
val = bld[(bld[V] >= 1000) & (bld[V] <= 200_000_000)].copy()   # meaningful-dollar building permits

print("Building permits total:", len(bld))
print("With meaningful valuation ($1k-$200M):", len(val),
      f"({len(val)/len(bld):.0%})")
print()

def money(x): return f"${x/1e9:,.2f}B" if abs(x) >= 1e9 else f"${x/1e6:,.1f}M"

# 1) Market by property class (meaningful-dollar building permits) ----
print("=== Building valuation & permit COUNT by Property Class (meaningful $) ===")
g = val.groupby("Property Class")[V].agg(["sum", "size"])
g["sum$"] = g["sum"].map(money)
print(g[["sum$", "size"]].to_string())
print("  (note: residential $ is understated — many new-home permits filed at $1 placeholder)")
print()

# 2) Valuation & counts by complete fiscal year -----------------------
print("=== By Fiscal Year (Building permits) ===")
comp_years = [2020, 2021, 2022, 2023, 2024, 2025]     # complete years
fy = val[val["Fiscal Year Issued"].isin(comp_years + [2026])].groupby("Fiscal Year Issued").agg(
    valuation=(V, "sum"), permits=(V, "size"))
fy["YoY_val%"] = fy["valuation"].pct_change()
out = fy.copy()
out["valuation"] = out["valuation"].map(money)
out["YoY_val%"] = out["YoY_val%"].map(lambda x: f"{x:+.0%}" if pd.notna(x) else "")
out.index = [f"FY{y}{' (partial)' if y==2026 else ''}" for y in out.index]
print(out.to_string())
print()

# 3) District opportunity — complete-year YoY (FY2024 vs FY2023) ------
print("=== District opportunity: Building valuation FY2024 vs FY2023 (complete years) ===")
def dv(y): return val[val["Fiscal Year Issued"] == y].groupby("Council District")[V].sum()
c = pd.DataFrame({"FY2023": dv(2023), "FY2024": dv(2024)}).fillna(0)
c = c[c.index != "Unknown"]
c["YoY%"] = (c["FY2024"] - c["FY2023"]) / c["FY2023"].replace(0, np.nan)
c = c.sort_values("FY2024", ascending=False)
disp = c.copy()
disp["FY2023"] = disp["FY2023"].map(money); disp["FY2024"] = disp["FY2024"].map(money)
disp["YoY%"] = disp["YoY%"].map(lambda x: f"{x:+.0%}" if pd.notna(x) else "n/a")
print(disp.to_string())
print()

# 4) Trade-permit counts by district (where contractor RELATIONSHIPS live)
print("=== Trade permits (Elec/Plumb/Mech) count by district, FY2024 vs FY2023 ===")
trades = df[df["Permit Type"].isin(["Electrical Permit","Plumbing Permit","Mechanical Permit"])]
def tc(y): return trades[trades["Fiscal Year Issued"]==y].groupby("Council District").size()
t = pd.DataFrame({"FY2023": tc(2023), "FY2024": tc(2024)}).fillna(0)
t = t[t.index != "Unknown"]
t["YoY%"] = (t["FY2024"]-t["FY2023"])/t["FY2023"].replace(0,np.nan)
t = t.sort_values("FY2024", ascending=False)
t["YoY%"] = t["YoY%"].map(lambda x: f"{x:+.0%}" if pd.notna(x) else "n/a")
print(t.astype({"FY2023":int,"FY2024":int}).to_string())
print()

# 5) Housing units added, complete years ------------------------------
print("=== Housing Units Added (Work Class = New), by Fiscal Year ===")
newu = df[df["Work Class"]=="New"].groupby("Fiscal Year Issued")["Housing Units"].sum()
print(newu.map(lambda x: f"{x:,.0f}").to_string())
print()

# 6) headline scalars -------------------------------------------------
print("=== Headline scalars (for KPI cards / narrative) ===")
print("Total permits (FY2020-2026):", f"{len(df):,}")
print("Total building valuation (meaningful $):", money(val[V].sum()))
print("Avg building project value (meaningful $):", f"${val[V].mean():,.0f}")
print("Median building project value (meaningful $):", f"${val[V].median():,.0f}")
