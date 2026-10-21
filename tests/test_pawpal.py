from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 10, 21)


@pytest.fixture
def owner():
    owner = Owner("Jordan")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Evening walk", "18:00", due_date=TODAY, priority="low"))
    mochi.add_task(Task("Morning walk", "08:00", due_date=TODAY, frequency="daily", priority="high"))
    luna.add_task(Task("Feeding", "12:30", due_date=TODAY, priority="medium"))
    return owner


def test_mark_complete_changes_status():
    task = Task("Walk", "08:00", due_date=TODAY)
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi")
    pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 1


def test_sort_by_time_is_chronological_across_pets(owner):
    times = [t.time for t in Scheduler(owner).sort_by_time()]
    assert times == ["08:00", "12:30", "18:00"]


def test_sort_by_priority_puts_high_first(owner):
    assert Scheduler(owner).sort_by_priority()[0].description == "Morning walk"


def test_filter_by_pet_and_status(owner):
    scheduler = Scheduler(owner)
    assert [t.description for t in scheduler.filter_tasks(pet_name="Luna")] == ["Feeding"]
    scheduler.owner.get_pet("Luna").tasks[0].mark_complete()
    assert scheduler.filter_tasks(pet_name="Luna", completed=False) == []


def test_daily_task_creates_next_day_occurrence(owner):
    scheduler = Scheduler(owner)
    walk = owner.get_pet("Mochi").tasks[1]
    next_task = scheduler.mark_task_complete(walk)
    assert next_task.due_date == TODAY + timedelta(days=1)
    assert next_task in owner.get_pet("Mochi").tasks


def test_one_off_task_does_not_recur(owner):
    feeding = owner.get_pet("Luna").tasks[0]
    assert Scheduler(owner).mark_task_complete(feeding) is None


def test_conflict_detected_for_same_time_across_pets(owner):
    owner.get_pet("Luna").add_task(Task("Medication", "08:00", due_date=TODAY))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1 and "08:00" in warnings[0]


def test_no_conflict_when_times_differ(owner):
    assert Scheduler(owner).detect_conflicts() == []


def test_pet_with_no_tasks_is_fine():
    owner = Owner("Sam")
    owner.add_pet(Pet("Empty"))
    assert Scheduler(owner).sort_by_time() == []


def test_next_available_slot_skips_busy_time(owner):
    owner.get_pet("Mochi").tasks[1].duration_minutes = 30
    assert Scheduler(owner).next_available_slot(TODAY, 15) == "08:30"


def test_json_round_trip(owner, tmp_path):
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)
    assert [t.description for t in loaded.get_all_tasks()] == [t.description for t in owner.get_all_tasks()]
    assert loaded.get_all_tasks()[0].due_date == TODAY
