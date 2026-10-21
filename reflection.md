# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- ***Briefly describe your initial UML design.***

I built four classes: `Task` (what/when), `Pet` (owns tasks), `Owner` (owns pets, `get_all_tasks()`), `Scheduler` (reads through the Owner so every feature spans all pets).

I thought of them as a chain where Owner has Pets, Pet has Tasks, and Scheduler sits on top and looks at everything.

| Class | What it knows (attributes) | What it does (methods) | Its one job |
|-------|---------------------------|------------------------|-------------|
| `Task` | description, time ("HH:MM"), due_date, frequency (once/daily/weekly), priority (low/medium/high), duration_minutes, completed, pet_name | `mark_complete()`, `start_minutes()`, `to_dict()` / `from_dict()` | Represent ONE activity and know how to repeat itself. |
| `Pet` | name, species, list of tasks | `add_task()`, `get_tasks()` | Own the tasks that belong to one animal. |
| `Owner` | name, list of pets | `add_pet()`, `get_pet()`, `get_all_tasks()`, `save_to_json()`, `load_from_json()` | Own the pets, and hand back every pet's tasks as one list. |
| `Scheduler` | the owner | `sort_by_time()`, `sort_by_priority()`, `filter_tasks()`, `mark_task_complete()`, `detect_conflicts()`, `next_available_slot()` | Be the "brain": organize and check tasks across ALL pets. |

- ***What classes did you include, and what responsibilities did you assign to each?***

As I said above, I included the dataclasses for Task, Pet, Owner as the spec and instructions suggested. Scheduler is a plain class because it holds behavior, not data.

***b. Design changes***

- ***Did your design change during implementation?***

Yes, the design changed as I ran into some problems that would throw an error and I would trace back to find the root cause. An example was that once tasks are pooled through `Owner.get_all_tasks()`, a task no longer knows which pet it belongs to, so filtering by pet, conflict messages ("Morning walk (Mochi)"), and recurrence could not work.

- ***If yes, describe at least one change and why you made it.***

My fix to the previous problem was simply to add `Pet.add_task()` which stamps the pet's name onto the task and allows the task to always have a pet name associated to it.

There were a few more problems that change the design. Here's a short list and their fixes:

1. `mark_complete()` **returns the next occurrence instead of adding it itself.** Problem: if Task added the new task to a pet it would need to know about Pet. Fix: Task just returns a fresh Task, and `Scheduler.mark_task_complete()` adds it to the right pet. This keeps Task simple and unaware of Pet.
2. **Task grew beyond the first UML.** The first UML only had description, time, frequency, completed. Added `due_date` (so "tomorrow's walk" is a different task from today's), `priority` and `duration_minutes` (the starter README required them).
3. **Conflict detection changed after the Codex review** (details in section 3): from "same start time" to "time ranges overlap".

---

## 2. Scheduling Logic and Tradeoffs

***a. Constraints and priorities***

- ***What constraints does your scheduler consider (for example: time, priority, preferences)?***

My scheduler considers the date and time of day, priority (high first), duration (used for overlaps and the free-slot finder), which pet, and whether it is done. Different combinations of these constraints change how the scheduler assigns tasks in the final build.

- ***How did you decide which constraints mattered most?***

I originally designed based on just time ordering (which is why it's the default view), because a pet owner's day runs in clock order. Then, Priority introduced an alternate view (`sort_by_priority`: high first, ties broken by time) for "what must not be skipped". Conflict warnings matter because they are the one thing the owner cannot see by just reading a list.

***b. Tradeoffs***

- ***Describe one tradeoff your scheduler makes.***

I made a tradeoff when designing `detect_conflicts()`. I had to how conflicts would be surfaced and if it would try to automatically move something. I decided that it would return warning text instead of moving a task without a user's approval. 

- ***Why is that tradeoff reasonable for this scenario?***

The reasoning was because the actual owner or real user of this app would knows things the app does not (an optional vet visit can wait, the walk cannot), and a warning cannot crash or silently reschedule a medication.

---

## 3. AI Collaboration

**a. How you used AI**

- ***How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?***

I did most of the brainstorming and design decisions and I had Claude help me with the actual work of implementing the code and building the UML, the classes, `main.py`, the tests, the Streamlit wiring, in phase order (UML, logic, demo, tests, UI, docs).

- ***What kinds of prompts or questions were most helpful?***

Feeding it a lot of up-front context and walking through myu decisions with a starting "interview" of my decisions and landing on a collaborative plan ended up benmefitting me because I was able to redesign things in a pointed manner rather than hoping a one-shot prompt worked in my favor. 

***b. Judgment and verification***

- ***Describe one moment where you did not accept an AI suggestion as-is.***

When I brought in Codex to review mine and Claude's work, Codex said conflict detection should skip pairs from the same pet (only check across pets). I rejected that because the spec says "same pet (or different pets)", and one pet cannot be walked and given medication at the same time, so same-pet clashes are exactly what the owner needs to see.

- ***How did you evaluate or verify what the AI suggested?***

I actually leverage AI to write test cases for the final build and created 15 pytest tests (three added for the Codex findings), running `main.py` and reading the output, and a headless Streamlit test that added a pet, added two same-time tasks, and checked the warning appeared.

---

## 4. Testing and Verification

**a. What you tested**

- ***What behaviors did you test?***

The 15 tests mentioned covered the following:

- Basics: completing a task changes its status; adding a task grows the pet's list.
- Sorting: chronological across two pets; high priority first.
- Filtering: by pet name and by completed/open.
- Recurrence: a daily task creates a task for the next day; a one-off task does not repeat; completing twice does not duplicate.
- Conflicts: same start time flagged; overlapping ranges flagged; back-to-back not flagged; no false alarm when times differ.
- Edge cases: a pet with no tasks; next free slot skips busy time; JSON save then load gives the same tasks and dates.
- ***Why were these tests important?***

These were important for testing silent failures like sorting, recurrence, and conflicts which are  three things that would silently give a pet owner a wrong day if they broke, without breaking the compiler or output on the frontend

***b. Confidence***

- ***How confident are you that your scheduler works correctly?***

I'm decently confident that the scheduler works and I'd rate it a 4 out of 5. The only downfall I didn't have time to fix was that conflicts ignore tasks that cross midnight, bad "HH:MM" input is not validated, and the browser look of the UI was not checked automatically.

- ***What edge cases would you test next if you had more time?***

I thought of some while developing but for the sake of time didn't get to test malformed times, weekly recurrence across a month end, two pets with the same name, a task with zero duration. I would tackle those first if I continued the project.

---

## 5. Reflection

***a. What went well***

- ***What part of this project are you most satisfied with?***

I was mostly satisified with my upfront planning which led to a clean implementation of all of my work and collaborating with Claude in a more effective manner.

**b. What you would improve**

- ***If you had another iteration, what would you improve or redesign?***

I would improve on the edge cases I identified above and defintiely would want to spend more time on deisng if I were, for any reason, developing this for widespread use. Then I'd tackle more tests, including a database, and take a more CRM approach with the scheduler as well. I would definitely redesign the frontend UI siunce I thnk it looks quite "AI-generated" because I was mainly focused on functionality throughout the project instead.

***c. Key takeaway***

- ***What is one important thing you learned about designing systems or working with AI on this project?***

The most important thing I learned is that if I treat the AI as a thought partner and start with my own design rather than let it generate all the decisions itself, it will work around my ideas and if it pushes back it's because there's genuinely an opportunity to improve my own approach. 
