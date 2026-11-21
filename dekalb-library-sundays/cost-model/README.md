# Cost model

`sunday-hours-cost-model.xlsx` estimates what it would cost to open every DeKalb County library on Sundays from noon to 5.

**These are the campaign's estimates.** DeKalb County Public Library has not published a figure. When it does, put its numbers in the Assumptions sheet.

## The answer

The campaign quotes a range: **$1.65 million to $2.1 million a year.**

| Way of working it out | Per year |
|---|---|
| **Base estimate:** new part-time staff, 25% Sunday differential | **$1,648,950** |
| The same plan with current staff on time and a half | $1,903,380 |
| Outside check: the library's current staffing cost per open hour | $1,784,007 |
| Outside check: Montgomery County, Maryland's Sunday staffing cost | $1,813,987 |
| The library's staffing cost per open hour, plus a Sunday differential | **$2,135,809** |
| Practical ceiling: the library's whole budget per open hour | $2,693,986 |

The base estimate is the lowest of these, which is why the public figure is a range and not a single number.

| | Base estimate | Top of range |
|---|---|---|
| Per resident per year | $2.15 | $2.78 |
| Share of the county General Fund | 0.27% | 0.35% |
| Share of the library's budget | 5.8% | 7.5% |
| First year, opening September 12, 2027 | $627,664 | $783,459 |
| Open hours gained | 115 a week, up 9.8% | the same |

The Summary sheet also shows Low and High columns ($0.8 million and $3.7 million). They set every assumption to its cheapest or dearest at once. The High figure is above the practical ceiling for that reason. Treat both as arithmetic limits, not forecasts.

## How to use it

Open the workbook in Excel, Numbers, Google Sheets or LibreOffice.

- **Assumptions** — change the blue numbers. Yellow cells matter most: staff on duty per branch, wages, and the Sunday pay differential.
- **Branches** — one row per location. Column D sets each branch's size tier from a drop-down.
- **Summary** — the results, with the planning range at the bottom. Nothing to edit.
- **Benchmarks** — five outside checks on the total.
- **Alternatives** — what a pilot, an hours swap, or weekday evening hours would cost instead.
- **Sources** — where each outside number came from.

Every result is a live formula.

## What drives the number

| Assumption | Base | Why it matters |
|---|---|---|
| Staff on duty per branch | 3 small, 4 medium, 6 large, 10 at Decatur | The largest driver, and our judgment. The library knows its real minimums |
| Who works the shifts | New part-time staff at a 25% differential | If current full-time staff work Sundays as overtime, the cost is about $250,000 higher |
| Benefits and payroll tax | 20% | Lower for part-time staff, higher for full-time |
| Security | One guard per branch, plus an officer at Decatur | About $240,000 a year |

## Known weak points

- **Shift leaders.** The model puts a librarian in charge at every branch. The library is unlikely to hire two dozen librarians for six hours a week, so current librarians would probably rotate. That is the time-and-a-half line above.
- **Support functions.** Nothing is included for technical or building support on Sundays beyond a 10% allowance for supervision and cover.
- **Utilities and cleaning** are a flat $120 per branch, the same for Decatur main as for the smallest location.
- **Start-up** is a flat $100,000 for recruiting and training.
- **Sundays per year** is 50. Most years have 52, a few have 53; Easter and holidays that fall on a Sunday are taken out. Each extra Sunday costs about $33,000.
- **Demand is unmeasured.** The cost-per-visit lines depend on an assumption about Sunday traffic.
- The two closest outside checks borrow this model's security and building costs, so they are independent on staffing only.

## One finding that cuts the other way

Weekday evening hours are cheaper per hour than Sunday hours (about $180 against $290 at the base estimate), because the building is already open and no differential applies. The argument for Sunday is about who can use the library then, not about price. See the Alternatives sheet.

## Rebuilding the workbook

```
python3 build_cost_model.py
```

Needs `openpyxl`. The script holds the branch list and every input, so changes made there are reproducible. Open the result in a spreadsheet program to recalculate.
