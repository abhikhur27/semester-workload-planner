# Semester Workload Planner

Practical Python CLI that turns a semester task backlog into a day-by-day work plan with urgency-aware scheduling.

## Why this project exists

When several courses have overlapping deadlines, ad-hoc planning usually underestimates risk. This tool gives a reproducible allocation plan from a single CSV, then flags any unplanned hours that did not fit the daily budget.

## Features

- Strict CSV schema validation (`task,course,due_date,estimated_hours,priority`)
- Priority + deadline-aware scoring per day
- Daily hour budget enforcement
- Explicit risk rows for overdue/unplanned workload
- Optional CSV export for calendar imports or spreadsheet review

## Usage

```bash
python planner.py --tasks sample_tasks.csv --start-date 2026-06-01 --daily-hours 3 --output plan.csv
```

## Example output snippet

```text
Semester Workload Planner
- Start date: 2026-06-01
- Daily budget: 3.0h
- Tasks loaded: 5
- Estimated hours: 24.0
...
```

## Input format

```csv
task,course,due_date,estimated_hours,priority
Exam 1 Review,CS3377,2026-06-05,7,5
```

## Sanity check

```bash
python planner.py --tasks sample_tasks.csv --start-date 2026-06-01 --daily-hours 3
python -m py_compile planner.py
```

## Portfolio Positioning

- Project type: Python command-line utility for real student workflow planning.
- Best use case: quickly drafting a defensible weekly plan before exam clusters.
- Future direction: export to `.ics` calendar format and add weekend/weekday budget profiles.
- Current status: incubation only (not listed on main portfolio homepage).
- Build tracker: see `DEVELOPMENT_CYCLE.md` for the multi-day quality plan.
