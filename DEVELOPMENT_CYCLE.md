# Development Cycle Tracker: Semester Workload Planner

Status: Incubation (not portfolio-listed)
Last updated: 2026-05-30

## North-Star Quality Bar

Goal: raise this from a useful script into a hiring/YC-grade product candidate.

Definition of done for listing:

- clear user persona and recurring workflow validated
- production-like UX path (CLI + optional app surface)
- robust input handling and edge-case behavior
- tests and benchmarked reliability on realistic workloads
- strong README with architecture + tradeoff rationale
- evidence of repeat value (not a one-off demo)

## Multi-Day Plan

## Day 1 - Problem Hardening

- Define primary persona (student with 4-6 concurrent classes).
- Document top failure modes of current planner output.
- Expand sample datasets (light/medium/heavy course loads).
- Output: `docs/problem-spec.md` + acceptance criteria.

## Day 2 - Scheduling Quality

- Improve allocation heuristic (avoid over-fragmented 1h chunks).
- Add configurable constraints: no-study days, max task split count.
- Add overdue penalty and risk-exposure scoring.
- Output: higher-quality plan consistency across datasets.

## Day 3 - Reliability + Tests

- Add unit tests for parsing, scoring, and allocation invariants.
- Add regression fixtures for edge cases (invalid CSV, impossible schedules).
- Add CI workflow for automated test runs.
- Output: stable test suite and repeatable quality checks.

## Day 4 - Product Surface

- Add optional TUI or small local web view for plan review.
- Add actionable summary ("what to do today", "what is at risk").
- Add export modes suited for real workflow (CSV + calendar import path).
- Output: stronger product feel beyond raw CLI output.

## Day 5 - Portfolio/Investor Readiness

- Add architecture section and tradeoff notes in README.
- Add clear before/after examples that show measurable user value.
- Write a concise product narrative: problem, wedge, expansion path.
- Output: final quality review against publish gate.

## Current Verdict (2026-05-30)

Not ready for portfolio homepage.

Why:

- useful but still script-level
- missing robustness proof and productized workflow
- lacks strong differentiation signal vs other lightweight utilities

Re-evaluation trigger:

Complete Day 1-5 outputs and pass all publish-gate items in portfolio project notes.
