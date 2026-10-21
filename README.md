# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit app and Python logic layer that helps a busy pet owner plan care tasks (walks, feeding, medication, grooming) across several pets, with smart ordering, conflict warnings, and recurring tasks.

## Features

- Owners, pets, and tasks modeled as classes (`Owner`, `Pet`, `Task`) with a `Scheduler` that works across every pet.
- Sort by time or by priority, filter by pet or status, daily and weekly recurrence, conflict warnings, and a "next free slot" finder.
- Data persists between runs in `data.json`.
- Streamlit UI plus a CLI demo (`main.py`) that exercises the same logic.

## How the classes work together

| Class | Responsibility |
|-------|----------------|
| `Task` | One activity: description, `HH:MM` time, date, frequency, priority, duration, completion. `mark_complete()` returns the next occurrence for recurring tasks. |
| `Pet` | Name, species, and its own task list (`add_task`, `get_tasks`). |
| `Owner` | Holds many pets. `get_all_tasks()` returns every pet's tasks together; `save_to_json` / `load_from_json` handle persistence. |
| `Scheduler` | The brain. Reads from `Owner.get_all_tasks()` so every feature works across all pets. |

UML source: `diagrams/uml.mmd` (draft) and `diagrams/uml_final.mmd` (matches the final code).

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py             # CLI demo
streamlit run app.py       # web UI
python -m pytest           # tests
```

## 🖥️ Sample Output

Output of `python main.py`:

```

Today's Schedule (sorted by time)
Time   Pet        Task                Min  Pri  Status
--------------------------------------------------------
08:00  🐶 Mochi    Morning walk         30  🔴   ⏳ open
08:00  🐱 Luna     Give medication       5  🔴   ⏳ open
12:30  🐱 Luna     Feeding              10  🟡   ⏳ open
18:00  🐶 Mochi    Evening walk         30  🟡   ⏳ open
19:00  🐱 Luna     Brush fur            15  🟢   ⏳ open

By priority, then time
Time   Pet        Task                Min  Pri  Status
--------------------------------------------------------
08:00  🐶 Mochi    Morning walk         30  🔴   ⏳ open
08:00  🐱 Luna     Give medication       5  🔴   ⏳ open
12:30  🐱 Luna     Feeding              10  🟡   ⏳ open
18:00  🐶 Mochi    Evening walk         30  🟡   ⏳ open
19:00  🐱 Luna     Brush fur            15  🟢   ⏳ open

Luna's tasks only
Time   Pet        Task                Min  Pri  Status
--------------------------------------------------------
08:00  🐱 Luna     Give medication       5  🔴   ⏳ open
12:30  🐱 Luna     Feeding              10  🟡   ⏳ open
19:00  🐱 Luna     Brush fur            15  🟢   ⏳ open

Conflict check:
  ⚠️  Conflict on 2026-10-21: Morning walk (Mochi, 08:00 for 30 min) overlaps Give medication (Luna, 08:00)

Completed 'Morning walk'. Next occurrence: 2026-10-22 at 08:00

Open tasks after completing one (tomorrow's walk is queued)
Time   Pet        Task                Min  Pri  Status
--------------------------------------------------------
08:00  🐱 Luna     Give medication       5  🔴   ⏳ open
12:30  🐱 Luna     Feeding              10  🟡   ⏳ open
18:00  🐶 Mochi    Evening walk         30  🟡   ⏳ open
19:00  🐱 Luna     Brush fur            15  🟢   ⏳ open
08:00  🐶 Mochi    Morning walk         30  🔴   ⏳ open

Next free 20 minute slot today: 08:05
Saved and reloaded 6 tasks for Jordan from data.json
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The 15 tests cover: task completion, adding a task to a pet, chronological sorting across pets, priority sorting, filtering by pet and status, daily recurrence (next task lands on the following day), one-off tasks not recurring, conflict detection (same start, overlapping ranges, back-to-back tasks not flagged), a pet with no tasks, next-available-slot, and completing a recurring task twice not duplicating it, and a JSON save/load round trip.

```
============================= test session starts ==============================
platform darwin -- Python 3.11.7, pytest-9.1.1, pluggy-1.7.0
plugins: anyio-4.15.1
collected 15 items

tests/test_pawpal.py ...............                                     [100%]

============================== 15 passed in 0.02s ==============================
```

Confidence level: ⭐⭐⭐⭐ (4/5). Core behaviors and the main edge cases pass; conflicts compare time ranges but ignore tasks that cross midnight, and there is no input validation for malformed `HH:MM` strings outside the UI.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Time sort uses `(due_date, "HH:MM")` as the key, which sorts correctly because times are zero padded. Priority sort puts high first, then time. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Either filter can be omitted. Works across all pets. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings (never raises) for open tasks on the same date whose time ranges overlap (start + duration), within or across pets. Shown with `st.warning` in the UI. |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Daily adds 1 day, weekly adds 7 days via `timedelta`; the new task is added to the same pet. |
| Next free slot | `Scheduler.next_available_slot()` | Walks the day's open tasks by start time and returns the earliest gap that fits the requested duration (08:00 to 20:00 window). |

## Optional extensions completed

- **Advanced algorithmic capability:** `Scheduler.next_available_slot()` (agent workflow documented in `ai_interactions.md`).
- **Data persistence:** `Owner.save_to_json()` and `Owner.load_from_json()` in `pawpal_system.py`. `app.py` loads `data.json` into `st.session_state` on first run and saves after every change; `main.py` demonstrates a save and reload. `data.json` is git-ignored. Files modified: `pawpal_system.py`, `app.py`, `main.py`, `tests/test_pawpal.py`.
- **Advanced priority scheduling:** `Task.priority` (low, medium, high) and `Scheduler.sort_by_priority()`; the "By priority, then time" table in the CLI output above shows it.
- **Multi-model prompt comparison:** Claude vs OpenAI Codex (`gpt-5.6-terra`) on recurrence and conflict logic; two of its suggestions were adopted (overlap-based conflicts, idempotent completion) and one rejected. Full table in `ai_interactions.md`.
- **Professional output formatting:** `main.py` prints an aligned table using f-string column widths with emoji for species (🐶 🐱), priority (🔴 🟡 🟢), and status (✅ ⏳); the UI uses the same icons. No external library was needed.

## 📸 Demo Walkthrough

1. Run `streamlit run app.py`. The owner is created once and stored in `st.session_state`, so data survives button clicks (and `data.json` keeps it across restarts).
2. Add a pet in the "Add a pet" form (for example Mochi the dog, then Luna the cat).
3. Schedule tasks in the "Schedule a task" form: pick the pet, description, time, minutes, priority, and repeat frequency.
4. Add two tasks at the same time for different pets and a yellow conflict warning appears above the schedule.
5. Use the Pet, Status, and Order dropdowns to filter and re-sort the schedule (by time or by priority).
6. Click "Mark done" on a daily task: it flips to ✅ and tomorrow's occurrence appears automatically.
7. Click "Next available slot today" to see the earliest free gap for a task of a given length.

Key Scheduler behaviors shown: sorting, filtering across pets, conflict warnings, recurrence, and slot finding. The CLI output above is from `main.py`.
