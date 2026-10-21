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
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
