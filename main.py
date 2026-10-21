"""CLI demo for the PawPal+ logic layer."""

from pawpal_system import Owner, Pet, Scheduler, Task

PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
SPECIES_ICON = {"dog": "🐶", "cat": "🐱"}


def print_schedule(title: str, tasks: list[Task], owner: Owner) -> None:
    """Print tasks as a readable table with status and priority icons."""
    print(f"\n{title}")
    print(f"{'Time':<6} {'Pet':<10} {'Task':<18} {'Min':>4}  {'Pri':<4} Status")
    print("-" * 56)
    for task in tasks:
        species = owner.get_pet(task.pet_name).species
        pet = f"{SPECIES_ICON.get(species, '🐾')} {task.pet_name}"
        status = "✅ done" if task.completed else "⏳ open"
        print(
            f"{task.time:<6} {pet:<10} {task.description:<18} {task.duration_minutes:>4}  "
            f"{PRIORITY_ICON[task.priority]:<3} {status}"
        )


def main() -> None:
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of order on purpose, with one deliberate time clash at 08:00.
    mochi.add_task(Task("Evening walk", "18:00", frequency="daily", priority="medium", duration_minutes=30))
    mochi.add_task(Task("Morning walk", "08:00", frequency="daily", priority="high", duration_minutes=30))
    luna.add_task(Task("Give medication", "08:00", priority="high", duration_minutes=5))
    luna.add_task(Task("Feeding", "12:30", frequency="daily", priority="medium", duration_minutes=10))
    luna.add_task(Task("Brush fur", "19:00", frequency="weekly", priority="low", duration_minutes=15))

    scheduler = Scheduler(owner)
    print_schedule("Today's Schedule (sorted by time)", scheduler.sort_by_time(), owner)
    print_schedule("By priority, then time", scheduler.sort_by_priority(), owner)
    print_schedule("Luna's tasks only", scheduler.filter_tasks(pet_name="Luna"), owner)

    print("\nConflict check:")
    for warning in scheduler.detect_conflicts():
        print(f"  ⚠️  {warning}")

    first_walk = scheduler.sort_by_time()[0]
    next_task = scheduler.mark_task_complete(first_walk)
    print(f"\nCompleted '{first_walk.description}'. Next occurrence: {next_task.due_date} at {next_task.time}")
    open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    print_schedule("Open tasks after completing one (tomorrow's walk is queued)", open_tasks, owner)

    slot = scheduler.next_available_slot(first_walk.due_date, 20)
    print(f"\nNext free 20 minute slot today: {slot}")

    owner.save_to_json("data.json")
    reloaded = Owner.load_from_json("data.json")
    print(f"Saved and reloaded {len(reloaded.get_all_tasks())} tasks for {reloaded.name} from data.json")


if __name__ == "__main__":
    main()
