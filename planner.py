#!/usr/bin/env python3
"""Semester Workload Planner CLI.

Builds a day-by-day study/work plan from a task CSV using urgency and effort balancing.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Task:
    name: str
    due_date: dt.date
    hours: float
    priority: int
    course: str


@dataclass
class Allocation:
    date: dt.date
    task_name: str
    course: str
    hours: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a workload plan from task CSV input.")
    parser.add_argument("--tasks", required=True, help="Path to tasks CSV.")
    parser.add_argument("--start-date", default=dt.date.today().isoformat(), help="Plan start date (YYYY-MM-DD).")
    parser.add_argument("--daily-hours", type=float, default=3.0, help="Max allocatable hours per day.")
    parser.add_argument(
        "--weekend-hours",
        type=float,
        help="Optional Saturday/Sunday hour budget override when weekends are included.",
    )
    parser.add_argument(
        "--skip-weekends",
        action="store_true",
        help="Plan only on weekdays so Saturday/Sunday stay clear unless work spills into risk rows.",
    )
    parser.add_argument("--output", help="Optional output CSV path for the generated plan.")
    parser.add_argument("--daily-summary-output", help="Optional CSV path for per-day planned/risk hour totals.")
    return parser.parse_args()


def parse_date(raw: str) -> dt.date:
    try:
        return dt.date.fromisoformat(raw.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid date '{raw}'. Expected YYYY-MM-DD.") from exc


def load_tasks(path: Path) -> list[Task]:
    if not path.exists():
        raise FileNotFoundError(f"Tasks file not found: {path}")

    tasks: list[Task] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = {"task", "course", "due_date", "estimated_hours", "priority"}
        if not reader.fieldnames or set(reader.fieldnames) != expected:
            raise ValueError(
                "CSV columns must be exactly: task,course,due_date,estimated_hours,priority"
            )

        for row in reader:
            name = row["task"].strip()
            course = row["course"].strip()
            if not name:
                raise ValueError("Task names cannot be empty.")
            if not course:
                course = "General"

            due_date = parse_date(row["due_date"])
            try:
                hours = float(row["estimated_hours"])
            except ValueError as exc:
                raise ValueError(f"Invalid estimated_hours for '{name}'.") from exc
            if hours <= 0:
                raise ValueError(f"Task '{name}' must have positive estimated_hours.")

            try:
                priority = int(row["priority"])
            except ValueError as exc:
                raise ValueError(f"Invalid priority for '{name}'.") from exc
            if priority < 1 or priority > 5:
                raise ValueError(f"Task '{name}' priority must be between 1 and 5.")

            tasks.append(Task(name=name, due_date=due_date, hours=hours, priority=priority, course=course))

    if not tasks:
        raise ValueError("No tasks found in CSV.")
    return tasks


def daterange(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)


def score_task(task: Task, day: dt.date) -> float:
    days_left = max((task.due_date - day).days, 0)
    urgency = 1 / (days_left + 1)
    workload = min(task.hours / 6.0, 1.0)
    priority_weight = task.priority / 5.0
    return (0.55 * urgency) + (0.3 * priority_weight) + (0.15 * workload)


def build_plan(
    tasks: list[Task],
    start_date: dt.date,
    daily_hours: float,
    skip_weekends: bool = False,
    weekend_hours: float | None = None,
) -> list[Allocation]:
    if daily_hours <= 0:
        raise ValueError("daily-hours must be positive.")
    if weekend_hours is not None and weekend_hours < 0:
        raise ValueError("weekend-hours cannot be negative.")

    mutable = [Task(**vars(task)) for task in tasks]
    last_due = max(task.due_date for task in mutable)
    if start_date > last_due:
        raise ValueError("start-date is after all task due dates.")

    allocations: list[Allocation] = []

    for day in daterange(start_date, last_due):
        if skip_weekends and day.weekday() >= 5:
            continue
        budget = weekend_hours if weekend_hours is not None and day.weekday() >= 5 else daily_hours
        candidates = [task for task in mutable if task.hours > 0 and task.due_date >= day]
        while budget > 1e-9 and candidates:
            candidates.sort(key=lambda task: score_task(task, day), reverse=True)
            selected = candidates[0]
            chunk = min(1.0, selected.hours, budget)
            selected.hours -= chunk
            budget -= chunk
            allocations.append(Allocation(date=day, task_name=selected.name, course=selected.course, hours=chunk))
            candidates = [task for task in mutable if task.hours > 0 and task.due_date >= day]

    # Spill unresolved work as risk rows on due dates.
    unresolved = [task for task in mutable if task.hours > 1e-9]
    for task in unresolved:
        allocations.append(
            Allocation(
                date=task.due_date,
                task_name=f"RISK: {task.name} (unplanned)",
                course=task.course,
                hours=round(task.hours, 2),
            )
        )

    allocations.sort(key=lambda row: (row.date, row.task_name))
    return allocations


def print_summary(
    tasks: list[Task],
    allocations: list[Allocation],
    start_date: dt.date,
    daily_hours: float,
    skip_weekends: bool,
    weekend_hours: float | None,
) -> None:
    total_hours = sum(task.hours for task in tasks)
    plan_hours = sum(item.hours for item in allocations if not item.task_name.startswith("RISK:"))
    risk_hours = sum(item.hours for item in allocations if item.task_name.startswith("RISK:"))

    print("Semester Workload Planner")
    print(f"- Start date: {start_date.isoformat()}")
    print(f"- Daily budget: {daily_hours:.1f}h")
    if not skip_weekends and weekend_hours is not None:
        print(f"- Weekend budget: {weekend_hours:.1f}h")
    print(f"- Scheduling mode: {'Weekdays only' if skip_weekends else 'All days'}")
    print(f"- Tasks loaded: {len(tasks)}")
    print(f"- Estimated hours: {total_hours:.1f}")
    print(f"- Planned hours: {plan_hours:.1f}")
    print(f"- Unplanned risk hours: {risk_hours:.1f}")

    course_rollup: dict[str, dict[str, float]] = {}
    for task in tasks:
        course_rollup.setdefault(task.course, {"estimated": 0.0, "planned": 0.0, "risk": 0.0})
        course_rollup[task.course]["estimated"] += task.hours
    for row in allocations:
        course_rollup.setdefault(row.course, {"estimated": 0.0, "planned": 0.0, "risk": 0.0})
        bucket = "risk" if row.task_name.startswith("RISK:") else "planned"
        course_rollup[row.course][bucket] += row.hours

    print("\nCourse rollup:")
    for course, totals in sorted(course_rollup.items()):
        print(
            f"  {course:<12} | est {totals['estimated']:.1f}h | "
            f"planned {totals['planned']:.1f}h | risk {totals['risk']:.1f}h"
        )

    print("\nNext 10 allocations:")
    for row in allocations[:10]:
        print(f"  {row.date.isoformat()} | {row.course:<8} | {row.task_name:<40} | {row.hours:.1f}h")


def write_output(path: Path, allocations: list[Allocation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "course", "task", "hours"])
        for row in allocations:
            writer.writerow([row.date.isoformat(), row.course, row.task_name, f"{row.hours:.2f}"])


def write_daily_summary(path: Path, allocations: list[Allocation]) -> None:
    daily: dict[dt.date, dict[str, float]] = {}
    for row in allocations:
        bucket = daily.setdefault(row.date, {"planned_hours": 0.0, "risk_hours": 0.0})
        if row.task_name.startswith("RISK:"):
            bucket["risk_hours"] += row.hours
        else:
            bucket["planned_hours"] += row.hours

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "planned_hours", "risk_hours", "total_hours"])
        for day in sorted(daily):
            planned = daily[day]["planned_hours"]
            risk = daily[day]["risk_hours"]
            writer.writerow([day.isoformat(), f"{planned:.2f}", f"{risk:.2f}", f"{planned + risk:.2f}"])


def main() -> None:
    args = parse_args()
    start_date = parse_date(args.start_date)
    tasks = load_tasks(Path(args.tasks))
    allocations = build_plan(
        tasks,
        start_date,
        args.daily_hours,
        skip_weekends=args.skip_weekends,
        weekend_hours=args.weekend_hours,
    )
    print_summary(
        tasks,
        allocations,
        start_date,
        args.daily_hours,
        skip_weekends=args.skip_weekends,
        weekend_hours=args.weekend_hours,
    )

    if args.output:
        output_path = Path(args.output)
        write_output(output_path, allocations)
        print(f"\nWrote plan CSV: {output_path}")

    if args.daily_summary_output:
        daily_summary_path = Path(args.daily_summary_output)
        write_daily_summary(daily_summary_path, allocations)
        print(f"Wrote daily summary CSV: {daily_summary_path}")


if __name__ == "__main__":
    main()
