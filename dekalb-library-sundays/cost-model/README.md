# Cost model

`sunday-hours-cost-model.xlsx` estimates what it would cost to open every DeKalb County library on Sundays from noon to 5.

**These are the campaign's estimates.** DeKalb County Public Library has not published a figure. When it does, put its numbers in the Assumptions sheet.

## The answer, base case

| | |
|---|---|
| Cost per year | **$1,648,950** |
| Cost of one Sunday, all 23 locations | $32,979 |
| Per resident per year | $2.15 |
| Share of the library's budget | 5.8% |
| Share of the county General Fund | 0.27% |
| Open hours gained | 115 a week, up 9.8% |
| First year, opening September 12, 2027 | $627,664 |

Two estimates that do not use the model's staffing assumptions land close by: $1.78 million using the library's current staffing cost per open hour, and $1.81 million using what Montgomery County, Maryland saved when it ended Sunday hours. The upper bound is $2.7 million.

Low and High ($0.8 million and $3.6 million) set every assumption to its cheapest or dearest at the same time. Treat them as outer limits.

## How to use it

Open the workbook in Excel, Numbers, Google Sheets or LibreOffice.

- **Assumptions** — change the blue numbers. Yellow cells matter most: staff on duty per branch, wages, and the Sunday pay differential.
- **Branches** — one row per location. Column D sets each branch's size tier from a drop-down.
- **Summary** — the results. Nothing to edit.
- **Benchmarks** — five outside checks on the total.
- **Alternatives** — what a pilot, an hours swap, or weekday evening hours would cost instead.
- **Sources** — where each outside number came from.

Every result is a live formula.

## What drives the number

| Assumption | Base | Why it matters |
|---|---|---|
| Staff on duty per branch | 3 small, 4 medium, 6 large, 10 at Decatur | The largest single driver. These are our judgment; the library knows its real minimums |
| Sunday pay differential | 25% | Makes Sunday shifts voluntary and attractive. Removing it saves about $250,000 a year |
| Benefits and payroll tax | 20% | Lower if Sunday shifts are filled by part-time staff, higher if by full-time staff |
| Security | One guard per branch, plus an officer at Decatur | About $240,000 a year |

## One finding that cuts the other way

Weekday evening hours are cheaper per hour than Sunday hours (about $180 against $290 in the base case), because the building is already open and no differential applies. The argument for Sunday is about who can use the library then, not about price. See the Alternatives sheet.

## Rebuilding the workbook

```
python3 build_cost_model.py
```

Needs `openpyxl`. The script holds the branch list and every input, so changes made there are reproducible.
