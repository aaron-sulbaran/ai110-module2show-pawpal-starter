# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Using Claude Code as the agent, I asked it to build PawPal+ end to end from the project spec: UML, the `pawpal_system.py` logic layer, a `main.py` demo, a pytest suite, the Streamlit wiring, and docs. The third algorithmic capability (the stretch feature) was `Scheduler.next_available_slot()`, which finds the earliest gap in a day's open tasks that fits a given duration.

**What did the agent do?**

- `pawpal_system.py`: wrote the `Task`, `Pet`, `Owner`, and `Scheduler` classes, including `next_available_slot`, priority sorting, recurrence, conflict detection, and JSON save/load.
- `main.py`: wrote the CLI demo and formatted output.
- `tests/test_pawpal.py`: wrote 12 tests, including one for `next_available_slot`.
- `app.py`: wired the UI to the classes with `st.session_state`, then ran a headless Streamlit `AppTest` smoke check (add pet, add two same-time tasks, confirm the conflict warning).
- `diagrams/uml.mmd`, `diagrams/uml_final.mmd`, `README.md`: wrote the diagrams and docs, pasting real `main.py` and pytest output.
- Made separate commits per stage (UML, logic, demo, tests, UI, docs).

**What did you have to verify or fix manually?**

- The agent's first run of the demo listed "open tasks" unsorted after a recurring task was completed, so tomorrow's walk appeared between today's tasks; it was fixed by sorting that list with `sort_by_time`.
- `pytest` was missing from the fresh virtual environment on the first test run and had to be installed from `requirements.txt`.
- <!-- Aaron: add anything you checked or changed yourself, e.g. ran the app and tried it, edited a docstring, rejected a suggestion -->

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Sonnet 5.5 via Claude Code (wrote the original `pawpal_system.py`) | OpenAI Codex CLI 0.163.0, model `gpt-5.6-terra`, read-only sandbox |
| **Prompt** | Build recurrence and conflict detection as part of the full PawPal+ spec | "Independently design (1) rescheduling of recurring daily/weekly tasks and (2) cross-pet conflict detection, writing your own code before reading mine. Then read `Task.mark_complete` and `Scheduler.detect_conflicts` and list where your design disagrees, ranked. Under 400 words. Do not edit files." |
| **Response summary** | Recurrence from the old `due_date` plus `timedelta`; conflicts grouped by exact `(date, "HH:MM")` slot. | Same recurrence rule, plus an `if self.completed: return None` guard. Conflicts by pairwise time-range overlap, skipping pairs from the same pet. |
| **What was useful** | Simple, readable, never raises. | Found that exact-time matching misses overlaps (a 30 min task at 08:00 and a task at 08:15 were not flagged), and that completing a recurring task twice created duplicate future tasks. Also confirmed scheduling from the previous due date (not today) avoids cadence drift. |
| **Problems noticed** | Exact-time conflicts were inconsistent with `next_available_slot`, which already used durations. No guard against double completion. | Its same-pet exclusion contradicts the spec ("same pet (or different pets)"), and it only listed generic conflict text with no times. |
| **Decision** | Kept the recurrence rule. | Adopted overlap-based conflict detection and the idempotent completion guard (3 new tests). Rejected the same-pet exclusion because a pet cannot be walked and medicated at once. |

**Which approach did you use in your final implementation and why?**

A hybrid. Recurrence stays as originally written plus Codex's idempotence guard. Conflict detection now compares start + duration ranges (Codex's idea) but still checks same-pet pairs (my original behavior, which matches the spec). Back-to-back tasks (one ends exactly when the next starts) are deliberately not conflicts. Verified with 15 passing tests.
