"""Build the Sunday-hours cost model workbook.

Run:  python3 build_cost_model.py
Writes sunday-hours-cost-model.xlsx next to this file. Every result in the
workbook is a live formula; this script only lays out inputs and formulas.
Needs openpyxl.
"""
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).with_name("sunday-hours-cost-model.xlsx")

FONT = "Arial"
BLUE = "0000FF"    # hard-coded input
GREEN = "008000"   # link to another sheet
BLACK = "000000"
YELLOW = PatternFill("solid", fgColor="FFFF00")
HEAD = PatternFill("solid", fgColor="1F3A5F")
BAND = PatternFill("solid", fgColor="E8EEF5")
THIN = Side(style="thin", color="B7C2D0")

USD = '$#,##0;($#,##0);-'
USD2 = '$#,##0.00;($#,##0.00);-'
NUM = '#,##0;(#,##0);-'
NUM1 = '#,##0.0;(#,##0.0);-'
PCT = '0.0%;(0.0%);-'
PCT2 = '0.00%;(0.00%);-'
MULT = '0.00"x"'
DATE = 'mmm d, yyyy'

# name, city, open hours per week today, size tier (the tier is our judgment)
BRANCHES = [
    ("Brookhaven", "Brookhaven", 48, "Small"),
    ("Chamblee", "Chamblee", 51, "Large"),
    ("Clarkston", "Clarkston", 51, "Medium"),
    ("County Line-Ellenwood", "Ellenwood", 51, "Medium"),
    ("Covington", "Decatur", 51, "Medium"),
    ("Decatur (main)", "Decatur", 60, "Central"),
    ("Doraville", "Doraville", 50, "Medium"),
    ("Dunwoody", "Dunwoody", 51, "Large"),
    ("Embry Hills", "Chamblee", 48, "Small"),
    ("Flat Shoals", "Decatur", 51, "Medium"),
    ("Gresham", "Atlanta", 48, "Small"),
    ("Hairston Crossing", "Stone Mountain", 51, "Medium"),
    ("Lithonia-Davidson", "Lithonia", 48, "Small"),
    ("Northlake-Barbara Loar", "Tucker", 51, "Medium"),
    ("Redan-Trotti", "Lithonia", 51, "Large"),
    ("Salem-Panola", "Stonecrest", 51, "Medium"),
    ("Scott Candler", "Decatur", 51, "Medium"),
    ("Scottdale-Tobie Grant Homework Center", "Scottdale", 50, "Small"),
    ("Stone Mountain-Sue Kellogg", "Stone Mountain", 51, "Medium"),
    ("Stonecrest", "Stonecrest", 51, "Large"),
    ("Toco Hill-Avis G. Williams", "Decatur", 51, "Large"),
    ("Tucker-Reid H. Cofer", "Tucker", 51, "Large"),
    ("Wesley Chapel-William C. Brown", "Decatur", 51, "Large"),
]

BUDGET = ("DeKalb County FY2026 Annual Budget as adopted Feb 26, 2026 "
          "(dekalbcountyga.gov), read Nov 21, 2026")
DCPL_STATS = "DCPL Statistics page, fiscal year July 2024-June 2025 (dekalblibrary.org/about-us/statistics), read Nov 21, 2026"


def style(cell, *, bold=False, color=BLACK, fmt=None, fill=None, wrap=False,
          align=None, italic=False, size=10):
    cell.font = Font(name=FONT, bold=bold, color=color, italic=italic, size=size)
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill
    if wrap or align:
        cell.alignment = Alignment(wrap_text=wrap, vertical="top", horizontal=align)
    return cell


def header_row(ws, row, labels):
    for col, text in enumerate(labels, start=1):
        c = ws.cell(row=row, column=col, value=text)
        style(c, bold=True, color="FFFFFF", fill=HEAD, wrap=True,
              align="left" if col == 1 else "center")
    ws.row_dimensions[row].height = 30


def section(ws, row, text, width):
    for col in range(1, width + 1):
        ws.cell(row=row, column=col).fill = BAND
    style(ws.cell(row=row, column=1, value=text), bold=True, fill=BAND)


def title(ws, text, sub):
    style(ws["A1"], bold=True, size=14).value = text
    style(ws["A2"], italic=True, color="555555", wrap=True).value = sub
    ws.row_dimensions[2].height = 42


# --------------------------------------------------------------------------
wb = Workbook()
ws_s = wb.active
ws_s.title = "Summary"
ws_a = wb.create_sheet("Assumptions")
ws_b = wb.create_sheet("Branches")
ws_k = wb.create_sheet("Benchmarks")
ws_x = wb.create_sheet("Alternatives")
ws_r = wb.create_sheet("Sources")

# ------------------------------------------------------------ Assumptions
title(ws_a, "Assumptions",
      "Edit the blue numbers. Yellow cells matter most. Low, Base and High are three complete "
      "sets of assumptions; every other sheet recalculates from them. These are the campaign's "
      "estimates until DeKalb County Public Library (DCPL) supplies its own figures.")
ws_a.merge_cells("A2:F2")
header_row(ws_a, 4, ["Assumption", "Low", "Base", "High", "Unit", "Source or reasoning"])

# (row, label, low, base, high, unit, note, fmt, key)
A = {}  # key -> row
rows = [
    ("sec", "Service"),
    ("hours", "Sunday public hours per branch", 5, 5, 5, "hours", "The ask: noon to 5 p.m.", NUM1, True),
    ("paid", "Paid hours per staff shift", 5.5, 6, 6.5, "hours", "Open hours plus time to open and close the building.", NUM1, False),
    ("sundays", "Sundays open per year", 50, 50, 52, "Sundays", "An average year has 52.1 Sundays. Less Easter and the occasional holiday that falls on a Sunday. Some years have 53.", NUM, False),
    ("sec", "Staff on duty at each branch on a Sunday"),
    ("small", "Small branch", 3, 3, 4, "people", "Campaign estimate. Replace with DCPL's minimum staffing by branch.", NUM, True),
    ("medium", "Medium branch", 3, 4, 5, "people", "Campaign estimate.", NUM, True),
    ("large", "Large branch", 5, 6, 8, "people", "Campaign estimate.", NUM, True),
    ("central", "Central (Decatur main)", 8, 10, 13, "people", "Campaign estimate.", NUM, True),
    ("lib", "Of those, librarians in charge: each branch", 1, 1, 1, "people", "One professional librarian leading each shift.", NUM, False),
    ("libc", "Of those, librarians in charge: Central", 1, 2, 2, "people", "Larger building, more service desks.", NUM, False),
    ("sec", "Pay"),
    ("wsup", "Support staff hourly wage", 19, 22, 26, "$ per hour", "County posting, Library Specialist Senior: $20.45-$32.93 an hour (2026). Base assumes a mix of grades.", USD2, True),
    ("wlib", "Librarian hourly wage", 26, 31, 36, "$ per hour", "County posting, Librarian grade 17: $52,266-$84,148 a year (March 2026), divided by 2,080 hours.", USD2, True),
    ("diff", "Sunday pay differential", 0, 0.25, 0.5, "% of wage", "Policy choice. The campaign recommends voluntary, premium-paid Sunday shifts.", PCT, True),
    ("load", "Payroll taxes and benefits", 0.08, 0.20, 0.38, "% of pay", "Low: part-time staff, payroll tax only. High: full-time staff with full benefits.", PCT, False),
    ("oh", "Supervision, scheduling and backfill", 0.05, 0.10, 0.15, "% of staff cost", "On-call manager, payroll and scheduling time, cover for absences.", PCT, False),
    ("sec", "Building and security"),
    ("guards", "Security guards per branch", 1, 1, 1, "people", "One guard at every open branch.", NUM, False),
    ("wguard", "Guard hourly rate", 25, 32, 45, "$ per hour", "Campaign estimate of a contract rate. Replace with the county's contract price.", USD2, False),
    ("police", "Police officers at Decatur", 1, 1, 1, "people", "County statement, Feb 11, 2026: an officer and a guard during all open hours at Decatur.", NUM, False),
    ("wpolice", "Police officer hourly rate", 45, 60, 75, "$ per hour", "Campaign estimate.", USD2, False),
    ("util", "Utilities and cleaning per branch per Sunday", 60, 120, 200, "$", "Campaign estimate of the added cost of opening a seventh day.", USD, False),
    ("sec", "Start-up and timing"),
    ("startup", "One-time start-up cost", 50000, 100000, 200000, "$", "Recruiting, training, signs, public notice.", USD, False),
    ("open", "Opening day (must be a Sunday)", None, date(2027, 9, 12), None, "date", "First Sunday after Labor Day 2027.", DATE, True),
    ("fye", "Last day of that fiscal year", None, date(2027, 12, 31), None, "date", "DeKalb's fiscal year is the calendar year.", DATE, False),
    ("sec", "Demand (used only for cost per visit)"),
    ("demand", "Sunday visits per open hour, compared with today's average", 0.6, 1.0, 1.3, "ratio", "Unknown until measured. One Illinois system reports Sunday as its busiest day per open hour; Seattle checkout data shows Sunday low.", MULT, True),
    ("sec", "County and library facts (one value, in the Base column)"),
    ("pop", "Service-area population", None, 768134, None, "people", DCPL_STATS, NUM, False),
    ("visits", "Library visits per year", None, 1723934, None, "visits", DCPL_STATS, NUM, False),
    ("libbud", "Library budget, FY2026", None, 28455984, None, "$", BUDGET + ", p. 176.", USD, False),
    ("info", "  of which Information Services", None, 7673311, None, "$", BUDGET + ", p. 176, cost center 06820.", USD, False),
    ("circ", "  of which Circulation", None, 7190712, None, "$", BUDGET + ", p. 176, cost center 06830.", USD, False),
    ("gf", "General Fund expenses, FY2026", None, 608352708, None, "$", BUDGET + ", General Fund financials.", USD, False),
    ("total", "Total county operating budget, FY2026", None, 1898108721, None, "$", BUDGET + ", expenditures by fund class.", USD, False),
    ("lib19", "Library budget, FY2019", None, 19690853, None, "$", BUDGET + ", table 'Tax Funds Budgets FY2019 vs FY2025'.", USD, False),
    ("gf19", "General Fund budget, FY2019", None, 357628941, None, "$", BUDGET + ", same table.", USD, False),
    ("sec", "Benchmark inputs"),
    ("moco", "Montgomery County, MD: Sunday positions cut", None, 624864, None, "$ per year", "Montgomery County FY2027 approved budget: 5.0 FTE abolished with the end of Sunday hours at 10 branches.", USD, False),
    ("mocon", "Montgomery County, MD: branches affected", None, 10, None, "branches", "Same source.", NUM, False),
    ("dk16", "DeKalb 2016 hours restoration: yearly cost", None, 2000000, None, "$ per year", "Atlanta Journal-Constitution, 2016: staff hired 'at an annualized cost of about $2 million'.", USD, False),
    ("dk16h", "DeKalb 2016 hours restoration: weekly hours added", None, 111, None, "hours per week", "Atlanta Journal-Constitution, 2016.", NUM, False),
    ("infl", "Price growth, 2016 to 2026", None, 1.35, None, "ratio", "Approximate consumer price change. Edit if you prefer a wage index.", MULT, False),
    ("uc", "Union City, CA: yearly payment to county library", None, 311056, None, "$ per year", "Alameda County board agenda, city-funded extra hours. Date about 2012; not adjusted for inflation.", USD, False),
    ("uch", "Union City, CA: weekly hours funded", None, 22, None, "hours per week", "Same source.", NUM, False),
    ("sec", "Sensitivity input"),
    ("ot", "Premium if existing full-time staff work Sundays as overtime", None, 0.5, None, "% of wage", "Time and a half. Used on the Summary sheet to show the cost if Sunday shifts are filled by current staff on overtime instead of new part-time staff.", PCT, False),
    ("sec", "Inputs for the Alternatives sheet"),
    ("pilot", "Pilot: number of branches", None, 6, None, "branches", "A typical counter-offer.", NUM, False),
    ("eve", "Evening alternative: hours added per branch per week", None, 6, None, "hours", "For example Thursday and Friday open until 8 instead of 5.", NUM, False),
]
r = 5
for item in rows:
    if item[0] == "sec":
        section(ws_a, r, item[1], 6)
        r += 1
        continue
    key, label, lo, base, hi, unit, note, fmt, important = item
    A[key] = r
    style(ws_a.cell(row=r, column=1, value=label), wrap=True)
    for col, val in ((2, lo), (3, base), (4, hi)):
        c = ws_a.cell(row=r, column=col, value=val)
        style(c, color=BLUE, fmt=fmt, fill=YELLOW if (important and val is not None) else None, align="right")
    style(ws_a.cell(row=r, column=5, value=unit), color="555555")
    style(ws_a.cell(row=r, column=6, value=note), color="555555", wrap=True)
    r += 1
# helper keys for the tier lookup (kept visible so the lookup is auditable)
style(ws_a.cell(row=4, column=7, value="Tier key"), bold=True, color="FFFFFF", fill=HEAD, align="center")
for key, name in (("small", "Small"), ("medium", "Medium"), ("large", "Large"), ("central", "Central")):
    style(ws_a.cell(row=A[key], column=7, value=name), color="555555", align="center")
for col, w in zip("ABCDEFG", (46, 13, 13, 13, 15, 78, 10)):
    ws_a.column_dimensions[col].width = w
ws_a.freeze_panes = "B5"


def a(key, col="C", absolute=True):
    """Reference an Assumptions cell from another sheet."""
    if absolute:
        return f"Assumptions!${col}${A[key]}"
    return f"Assumptions!{col}${A[key]}"


# ---------------------------------------------------------------- Branches
title(ws_b, "Cost by branch",
      "One row per location, from the library's own hours page (read Nov 21, 2026). The size tier "
      "in column D is the campaign's judgment: change it from the drop-down and the costs follow.")
ws_b.merge_cells("A2:P2")
header_row(ws_b, 4, [
    "Branch", "City", "Open hours per week today", "Size tier",
    "Staff on duty: Low", "Staff on duty: Base", "Staff on duty: High",
    "Librarians: Low", "Librarians: Base", "Librarians: High",
    "Cost of one Sunday: Low", "Cost of one Sunday: Base", "Cost of one Sunday: High",
    "Cost per year: Low", "Cost per year: Base", "Cost per year: High",
])
ws_b.row_dimensions[4].height = 44
first = 5
last = first + len(BRANCHES) - 1
tot = last + 1
tier_keys = f"Assumptions!$G${A['small']}:$G${A['central']}"
dv = DataValidation(type="list", formula1='"Small,Medium,Large,Central"', allow_blank=False)
ws_b.add_data_validation(dv)
for i, (name, city, hrs, tier) in enumerate(BRANCHES):
    row = first + i
    style(ws_b.cell(row=row, column=1, value=name))
    style(ws_b.cell(row=row, column=2, value=city))
    style(ws_b.cell(row=row, column=3, value=hrs), color=BLUE, fmt=NUM)
    c = style(ws_b.cell(row=row, column=4, value=tier), color=BLUE, fill=YELLOW, align="center")
    dv.add(c)
    # scenario column on Assumptions (B, C, D) lines up with staff (E, F, G), librarians (H, I, J)
    for k, scen in enumerate("BCD"):
        staff_col = "EFG"[k]
        lib_col = "HIJ"[k]
        sun_col = "KLM"[k]
        yr_col = "NOP"[k]
        rng = f"Assumptions!{scen}${A['small']}:{scen}${A['central']}"
        style(ws_b[f"{staff_col}{row}"], color=GREEN, fmt=NUM).value = (
            f"=INDEX({rng},MATCH($D{row},{tier_keys},0))")
        style(ws_b[f"{lib_col}{row}"], color=GREEN, fmt=NUM).value = (
            f'=IF($D{row}="Central",{a("libc", scen)},{a("lib", scen)})')
        staff = (f"{a('paid', scen)}*(1+{a('diff', scen)})*(1+{a('load', scen)})*(1+{a('oh', scen)})"
                 f"*({lib_col}{row}*{a('wlib', scen)}+({staff_col}{row}-{lib_col}{row})*{a('wsup', scen)})")
        security = (f"{a('paid', scen)}*({a('guards', scen)}*{a('wguard', scen)}"
                    f'+IF($D{row}="Central",{a("police", scen)}*{a("wpolice", scen)},0))')
        style(ws_b[f"{sun_col}{row}"], fmt=USD).value = f"={staff}+{security}+{a('util', scen)}"
        style(ws_b[f"{yr_col}{row}"], fmt=USD).value = f"={sun_col}{row}*{a('sundays', scen)}"
style(ws_b.cell(row=tot, column=1, value="All branches"), bold=True)
for col in "CEFGHIJKLMNOP":
    c = ws_b[f"{col}{tot}"]
    c.value = f"=SUM({col}{first}:{col}{last})"
    style(c, bold=True, fmt=NUM if col in "CEFGHIJ" else USD)
    c.border = Border(top=THIN)
ws_b[f"A{tot}"].border = Border(top=THIN)
ws_b[f"B{tot}"].border = Border(top=THIN)
ws_b[f"D{tot}"].border = Border(top=THIN)
ws_b["D4"].comment = Comment(
    "Tiers are the campaign's judgment, not DCPL's. Small = the locations DCPL itself schedules "
    "for 48 hours a week, plus the homework center. Large = the busier regional branches.", "Campaign")
for col, w in zip("ABCDEFGHIJKLMNOP", (36, 16, 12, 10, 9, 9, 9, 10, 10, 10, 13, 13, 13, 14, 14, 14)):
    ws_b.column_dimensions[col].width = w
ws_b.freeze_panes = "B5"

N_BR = f"COUNTA(Branches!$A${first}:$A${last})"
WK_HRS = f"Branches!$C${tot}"
# security + building for one year, base case (used by two benchmarks)
SEC_BLDG = (f"{a('sundays')}*({N_BR}*({a('paid')}*{a('guards')}*{a('wguard')}+{a('util')})"
            f"+{a('paid')}*{a('police')}*{a('wpolice')})")

# -------------------------------------------------------------- Benchmarks
title(ws_k, "Cross-checks against outside figures",
      "Five other ways to estimate the same thing. None uses this model's staffing assumptions, though "
      "checks 1 and 2 borrow its security and building costs. The base case sits below all of them, "
      "which is why the campaign quotes a range.")
ws_k.merge_cells("A2:C2")
header_row(ws_k, 4, ["Check", "Value", "How it is worked out"])
K = {}


def krow(row, key, label, formula, fmt, note, bold=False, link=False):
    K[key] = row
    style(ws_k.cell(row=row, column=1, value=label), bold=bold, wrap=True)
    style(ws_k.cell(row=row, column=2, value=formula), bold=bold, fmt=fmt,
          color=GREEN if link else BLACK)
    style(ws_k.cell(row=row, column=3, value=note), color="555555", wrap=True)


section(ws_k, 5, "1. Montgomery County, Maryland: what ending Sunday hours saved", 3)
krow(6, "m1", "Staff cost per branch per year", f"={a('moco')}/{a('mocon')}", USD, "Positions cut divided by branches affected.", link=True)
krow(7, "m2", "Applied to every DeKalb branch", f"=B6*{N_BR}", USD, "Staff only.")
krow(8, "m3", "Add security and building costs from this model", f"={SEC_BLDG}", USD, "Guards, the Decatur officer, utilities and cleaning, base case.", link=True)
krow(9, "m4", "Estimate", "=B7+B8", USD, "Likely an undercount: Montgomery also used existing staff on Sundays.", bold=True)
section(ws_k, 10, "2. DCPL's own staffing cost for an average open hour", 3)
krow(11, "s1", "Public-service staffing cost per branch-hour", f"=({a('info')}+{a('circ')})/({WK_HRS}*52)", USD2, "Information Services plus Circulation budgets, divided by all open hours in a year.", link=True)
krow(12, "s2", "Applied to the Sunday hours", f"=B11*{a('hours')}*{N_BR}*{a('sundays')}", USD, "Assumes Sunday is staffed like an average hour. An average hour includes programs and behind-the-scenes work, so this may overstate Sunday staffing.")
krow(13, "s3", "Add security and building costs from this model", "=B8", USD, "Same as above.")
krow(14, "s4", "Estimate, no Sunday differential", "=B12+B13", USD, "", bold=True)
krow(15, "s5", "Estimate, with this model's Sunday differential", f"=B12*(1+{a('diff')})+B13", USD, "The same check if Sunday staff are paid the differential. Top of the planning range.", bold=True)
section(ws_k, 16, "3. Practical ceiling: DCPL's whole budget per open hour", 3)
krow(17, "c1", "Whole library budget per branch-hour", f"={a('libbud')}/({WK_HRS}*52)", USD2, "Includes books, technology, administration and maintenance, most of which Sunday hours would not add to.", link=True)
krow(18, "c2", "Estimate (practical ceiling)", f"=B17*{a('hours')}*{N_BR}*{a('sundays')}", USD, "A realistic Sunday plan should not cost more than this. The High case on the Summary sheet does, because it stacks every pessimistic assumption.", bold=True)
section(ws_k, 19, "4. DeKalb's 2016 restoration of night and weekend hours", 3)
krow(20, "d1", "Cost per added branch-hour, 2016 dollars", f"={a('dk16')}/({a('dk16h')}*52)", USD2, "Included 36 full-time hires that also filled earlier staffing gaps.", link=True)
krow(21, "d2", "In today's dollars", f"=B20*{a('infl')}", USD2, "")
krow(22, "d3", "Estimate (upper bound)", f"=B21*{a('hours')}*{N_BR}*{a('sundays')}", USD, "", bold=True)
section(ws_k, 23, "5. Union City, California: what a city pays its county library for extra hours", 3)
krow(24, "u1", "Payment per weekly hour, per year", f"={a('uc')}/{a('uch')}", USD, "About 2012 dollars, not adjusted. Context only.", link=True)
krow(25, "u2", "Estimate", f"=B24*{a('hours')}*{N_BR}", USD, "", bold=True)
section(ws_k, 26, "How this model compares", 3)
krow(27, "base", "This model, base case", "=Summary!C6", USD, "From the Summary sheet.", bold=True, link=True)
krow(28, "r1", "Check 1 compared with the base case", "=IF(B27=0,0,B9/B27)", MULT, "Above 1.00x means the outside check is higher than the base case.")
krow(29, "r2", "Check 2 (no differential) compared with the base case", "=IF(B27=0,0,B14/B27)", MULT, "")
krow(30, "r3", "Check 2 (with differential) compared with the base case", "=IF(B27=0,0,B15/B27)", MULT, "")
krow(31, "r4", "Base case as a share of the practical ceiling", "=IF(B18=0,0,B27/B18)", PCT, "")
for col, w in zip("ABC", (58, 16, 88)):
    ws_k.column_dimensions[col].width = w

# ------------------------------------------------------------ Alternatives
title(ws_x, "What the county may offer instead",
      "The campaign's ask is every branch. This sheet prices the two likeliest counter-offers and "
      "one competing use of the money, so the campaign can say exactly what each gives up.")
ws_x.merge_cells("A2:C2")
header_row(ws_x, 4, ["Item", "Value", "What it means"])
WAGES = (f"(SUM(Branches!$I${first}:$I${last})*{a('wlib')}"
         f"+(SUM(Branches!$F${first}:$F${last})-SUM(Branches!$I${first}:$I${last}))*{a('wsup')})")


def xrow(row, label, formula, fmt, note, bold=False, link=False):
    style(ws_x.cell(row=row, column=1, value=label), bold=bold, wrap=True)
    style(ws_x.cell(row=row, column=2, value=formula), bold=bold, fmt=fmt,
          color=GREEN if link else BLACK)
    style(ws_x.cell(row=row, column=3, value=note), color="555555", wrap=True)


section(ws_x, 5, "A. A pilot at a few branches", 3)
xrow(6, "Branches in the pilot", f"={a('pilot')}", NUM, "Set on the Assumptions sheet.", link=True)
xrow(7, "Cost per year", "=B6*Summary!C7", USD, "Pilot branches at the average base cost per branch.", bold=True)
xrow(8, "Branches still closed on Sunday", f"={N_BR}-B6", NUM, "")
xrow(9, "Share of branches served", f"=B6/{N_BR}", PCT, "Someone has to choose which neighbourhoods wait.")
xrow(10, "Saving compared with every branch", "=Summary!C6-B7", USD, "")
section(ws_x, 11, "B. An hours swap: open Sunday by closing the same number of weekday hours", 3)
xrow(12, "Weekday hours given up per year", f"={a('hours')}*{N_BR}*{a('sundays')}", NUM, "Usually weekday mornings: story times, seniors, job seekers.")
xrow(13, "Cost that remains per year", f"={a('sundays')}*{a('paid')}*{a('diff')}*(1+{a('load')})*(1+{a('oh')})*{WAGES}", USD, "Only the Sunday pay differential is new money. Zero if no differential is paid.", bold=True)
xrow(14, "Net change in open hours", 0, NUM, "None. The county is open no more than it is today.")
section(ws_x, 15, "C. A competing use: later closing on weekdays instead of Sunday", 3)
xrow(16, "Hours added per week, all branches", f"={a('eve')}*{N_BR}", NUM, "For example Thursday and Friday until 8.")
xrow(17, "Cost of one staffed branch-hour on a weekday, all branches together", f"=(1+{a('load')})*(1+{a('oh')})*{WAGES}+{N_BR}*{a('guards')}*{a('wguard')}+{a('police')}*{a('wpolice')}", USD, "Same staffing as the Sunday base case, no differential, no added opening or closing time.")
xrow(18, "Cost per year", f"=B17*{a('eve')}*52", USD, "", bold=True)
xrow(19, "Cost per added branch-hour: weekday evenings", f"=IF(B16=0,0,B18/(B16*52))", USD2, "")
xrow(20, "Cost per added branch-hour: Sunday", "=Summary!C8", USD2, "From the Summary sheet.", link=True)
xrow(21, "What the comparison shows", None, None, "Evening hours usually cost less per hour: the building is already open and no Sunday differential applies. The case for Sunday rests on who it reaches, not on price.")
for col, w in zip("ABC", (62, 16, 84)):
    ws_x.column_dimensions[col].width = w

# ----------------------------------------------------------------- Summary
title(ws_s, "Sunday 12 to 5 at every DeKalb library: what it costs",
      "Estimates by the campaign, not by DeKalb County Public Library. Change the blue cells on the "
      "Assumptions sheet and everything here recalculates. Low and High put every assumption at its "
      "cheapest or dearest at once, so the true figure is unlikely to sit at either end. The planning "
      "range the campaign quotes is at the bottom of this sheet.")
ws_s.merge_cells("A2:E2")
header_row(ws_s, 4, ["", "Low", "Base", "High", "What it means"])


def srow(row, label, formulas, fmt, note, bold=False, link=False):
    style(ws_s.cell(row=row, column=1, value=label), bold=bold, wrap=True)
    for col, f in zip("BCD", formulas):
        style(ws_s[f"{col}{row}"], bold=bold, fmt=fmt, color=GREEN if link else BLACK,
              fill=YELLOW if (bold and col == "C") else None).value = f
    style(ws_s.cell(row=row, column=5, value=note), color="555555", wrap=True)


def per_scen(template):
    """Fill {s} with the Assumptions scenario column and {c} with this sheet's column."""
    return [template.format(s=s, c=c) for s, c in zip("BCD", "BCD")]


srow(5, "Cost of one Sunday, all branches", [f"=Branches!{c}{tot}" for c in "KLM"], USD, "Staff, security, utilities and cleaning.", link=True)
srow(6, "Cost per year, every year", [f"=Branches!{c}{tot}" for c in "NOP"], USD, "The headline number.", bold=True, link=True)
srow(7, "Average per branch per year", per_scen("={c}6/" + N_BR), USD, "")
srow(8, "Cost per added branch-hour", per_scen("={c}6/(Assumptions!{s}$%d*%s*Assumptions!{s}$%d)" % (A["hours"], N_BR, A["sundays"])), USD2, "")
section(ws_s, 9, "The first year, if every branch opens on the same day", 5)
srow(10, "Opening day", [None, f"={a('open')}", None], DATE, "Set on the Assumptions sheet.", link=True)
srow(11, "Sundays open in that fiscal year", [f"=INT(({a('fye')}-{a('open')})/7)+1"] * 3, NUM, "Opening day to the end of the fiscal year.")
srow(12, "First-year cost, including start-up", per_scen("={c}11*{c}5+Assumptions!{s}$%d" % A["startup"]), USD, "What the FY2027 budget would need.", bold=True)
section(ws_s, 13, "How big is that?", 5)
srow(14, "Per resident per year", per_scen("={c}6/" + a("pop")), USD2, "Yearly cost divided by the population DCPL serves.")
srow(15, "Share of the library's budget", per_scen("={c}6/" + a("libbud")), PCT, "")
srow(16, "Share of the General Fund", per_scen("={c}6/" + a("gf")), PCT2, "The fund that pays for the library.")
srow(17, "Share of the whole county operating budget", per_scen("={c}6/" + a("total")), PCT2, "")
section(ws_s, 18, "What residents get", 5)
srow(19, "Open hours per week today, all branches", [f"={WK_HRS}"] * 3, NUM, "From the library's hours page.", link=True)
srow(20, "Sunday hours added per week", per_scen("=Assumptions!{s}$%d*%s" % (A["hours"], N_BR)), NUM, "")
srow(21, "Increase in open hours", per_scen("={c}20/{c}19"), PCT, "Compare with the share of the library's budget above.")
section(ws_s, 22, "Value for money, at the base cost. Columns here are low, base and high Sunday demand", 5)
srow(23, "Visits per open branch-hour today", [f"={a('visits')}/({WK_HRS}*52)"] * 3, NUM1, "All visits divided by all open hours.", link=True)
srow(24, "Sunday visits per year", per_scen("={c}23*Assumptions!{s}$%d*$C$20*%s" % (A["demand"], a("sundays"))), NUM, "Depends on the demand assumption, which is unmeasured.")
srow(25, "Cost per Sunday visit", per_scen("=IF({c}24=0,0,$C$6/{c}24)"), USD2, "Base yearly cost divided by Sunday visits.")
srow(26, "Cost per visit today, whole library budget", [f"={a('libbud')}/{a('visits')}"] * 3, USD2, "For comparison.", link=True)
srow(27, "Sunday traffic needed to match today's cost per visit", ["=IF($C$23*$C$20*%s=0,0,($C$6/$C$26)/($C$23*$C$20*%s))" % (a("sundays"), a("sundays"))] * 3, PCT, "As a share of today's average hourly traffic.")
section(ws_s, 28, "The library's share of the General Fund", 5)
srow(29, "Share in FY2019", [None, f"={a('lib19')}/{a('gf19')}", None], PCT2, "", link=True)
srow(30, "Share in FY2026", [None, f"={a('libbud')}/{a('gf')}", None], PCT2, "", link=True)
srow(31, "Library budget today if the FY2019 share had held", [None, f"=C29*{a('gf')}", None], USD, "")
srow(32, "Gap to the actual budget", [None, f"=C31-{a('libbud')}", None], USD, "")
srow(33, "Sunday hours (base) as a share of that gap", [None, "=IF(C32=0,0,C6/C32)", None], PCT, "")
section(ws_s, 34, "Planning range (details on the Benchmarks sheet)", 5)
srow(35, "Base case: new part-time staff, 25% Sunday differential", [None, "=C6", None], USD, "Bottom of the planning range.", bold=True)
srow(36, "Base case if current staff work Sundays at time and a half", [None, f"=(C6-({SEC_BLDG}))*(1+{a('ot')})/(1+{a('diff')})+({SEC_BLDG})", None], USD, "Staff cost rescaled to the overtime premium on the Assumptions sheet.")
srow(37, "Outside check: Montgomery County, MD", [None, "=Benchmarks!B9", None], USD, "Staff cost from another system, plus this model's security and building costs.", link=True)
srow(38, "Outside check: DCPL's own staffing cost per open hour", [None, "=Benchmarks!B14", None], USD, "No Sunday differential.", link=True)
srow(39, "Same check with the Sunday differential", [None, "=Benchmarks!B15", None], USD, "Top of the planning range.", bold=True, link=True)
srow(40, "Practical ceiling: DCPL's whole budget per open hour", [None, "=Benchmarks!B18", None], USD, "The High case above exceeds this because it stacks every pessimistic assumption.", link=True)
srow(41, "Top of the range, per resident per year", [None, f"=C39/{a('pop')}", None], USD2, "")
srow(42, "Top of the range, share of the General Fund", [None, f"=C39/{a('gf')}", None], PCT2, "")
srow(43, "Top of the range, share of the library's budget", [None, f"=C39/{a('libbud')}", None], PCT, "")
srow(44, "Top of the range, first-year cost", [None, f"=C39/{a('sundays')}*C11+{a('startup')}", None], USD, "")
for col, w in zip("ABCDE", (56, 15, 15, 15, 70)):
    ws_s.column_dimensions[col].width = w
ws_s.freeze_panes = "B5"

# ----------------------------------------------------------------- Sources
title(ws_r, "Sources", "Where each outside number came from, and when it was read.")
ws_r.merge_cells("A2:C2")
header_row(ws_r, 4, ["Fact", "Source", "Link"])
sources = [
    ("Branch list and opening hours; all 23 locations closed Sunday", "DCPL locations page, read Nov 21, 2026", "https://dekalblibrary.org/locations"),
    ("Population served, visits, circulation, cardholders (FY2025)", "DCPL statistics page, read Nov 21, 2026", "https://dekalblibrary.org/about-us/statistics"),
    ("Library budget by cost center; General Fund; county totals; FY2019 comparison", "DeKalb County FY2026 Annual Budget as adopted Feb 26, 2026, pp. 2, 18-27, 176", "https://dekalbcountyga.gov/sites/default/files/2026-04/FY2026%20DeKalb%20County%20Annual%20Budget%20as%20adopted.pdf"),
    ("Budget calendar: CEO recommendation by Dec 15, adoption by Mar 1", "DeKalb County Office of Management and Budget, Budget Process page", "https://dekalbcountyga.gov/departments/budget/budget-process"),
    ("Librarian pay range $52,266-$84,148; Library Specialist Senior $20.45-$32.93 an hour", "DeKalb County job postings, 2026, as listed by job sites", "https://www.career.com/job/dekalb-county-ga/librarian/j202206030423033910349"),
    ("Police officer and guard at Decatur during all open hours", "DeKalb County news release, Feb 11, 2026", "https://dekalbcountyga.gov/news/2026-02-11/decatur-library-reopen-enhanced-security-protocols"),
    ("Montgomery County, MD: $624,864 and 5.0 FTE tied to ending Sunday hours at 10 branches", "Montgomery County FY2027 approved operating budget, Public Libraries", "https://apps.montgomerycountymd.gov/BASISOPERATING/Common/Department.aspx?ID=71D"),
    ("DeKalb 2016: $491,972 mid-year, 111 hours a week, about $2 million a year", "Atlanta Journal-Constitution, 2016", "https://www.ajc.com/news/local-govt--politics/dekalb-libraries-add-night-and-weekend-hours-2017/9HkuC8Eu22nIf3EhPJGL9N"),
    ("Union City, CA: $311,056 for 22 extra hours a week", "Alameda County Board of Supervisors agenda item", "http://www.acgov.org/board/bos_calendar/documents/DocsAgendaReg_09_13_11/GENERAL%20ADMINISTRATION/Regular%20Calendar/Library_City_Union_City.pdf"),
    ("Gwinnett: all 15 branches open Sunday noon to 5", "Gwinnett County news story on the library's consistent schedule", "https://www.gwinnettcounty.com/home/stories/viewstory/-/story/Librarysystemsnewhoursconsistentschedulein"),
]
for i, (fact, src, link) in enumerate(sources, start=5):
    style(ws_r.cell(row=i, column=1, value=fact), wrap=True)
    style(ws_r.cell(row=i, column=2, value=src), wrap=True)
    style(ws_r.cell(row=i, column=3, value=link), color="0563C1", wrap=True)
for col, w in zip("ABC", (60, 60, 80)):
    ws_r.column_dimensions[col].width = w

wb.save(OUT)
print("wrote", OUT)
