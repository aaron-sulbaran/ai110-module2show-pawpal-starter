"""PawPal+ logic layer: Owner, Pet, Task, and the Scheduler that works across pets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM", 24 hour
    due_date: date = field(default_factory=date.today)
    frequency: str = "once"  # once, daily, weekly
    priority: str = "medium"  # low, medium, high
    duration_minutes: int = 15
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done and return the next occurrence if it recurs."""
        if self.completed:
            return None
        self.completed = True
        step =FREQUENCY_DAYS.get(self.frequency)
        if step is None:
            return None
        return Task(
            description=self.description,
            time=self.time,
            due_date=self.due_date + timedelta(days=step),
            frequency=self.frequency,
            priority=self.priority,
            duration_minutes=self.duration_minutes,
            pet_name=self.pet_name,
        )

    def start_minutes(self) -> int:
        """Minutes after midnight that this task starts."""
        hours, minutes = self.time.split(":")
        return int(hours) * 60 + int(minutes)

    def to_dict(self) -> dict:
        """Convert to a JSON friendly dict."""
        data = asdict(self)
        data["due_date"] = self.due_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from to_dict output."""
        return cls(**{**data, "due_date": date.fromisoformat(data["due_date"])})


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str
    species: str = "dog"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    """A person who owns one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name, or None."""
        return next((pet for pet in self.pets if pet.name == name), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every pet's tasks together."""
        return [task for pet in self.pets for task in pet.tasks]

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Write the owner, pets, and tasks to a JSON file."""
        payload = {
            "name": self.name,
            "pets": [
                {"name": p.name, "species": p.species, "tasks": [t.to_dict() for t in p.tasks]}
                for p in self.pets
            ],
        }
        Path(path).write_text(json.dumps(payload, indent=2))

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> "Owner":
        """Read an owner back from save_to_json output."""
        payload = json.loads(Path(path).read_text())
        pets = [
            Pet(p["name"], p["species"], [Task.from_dict(t) for t in p["tasks"]])
            for p in payload["pets"]
        ]
        return cls(payload["name"], pets)


class Scheduler:
    """The brain: organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Sort tasks by due date, then by HH:MM time."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def sort_by_priority(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Sort by priority (high first), then by due date and time."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.due_date, t.time))

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> list[Task]:
        """Filter all tasks by pet name and/or completion status."""
        return [
            t
            for t in self.owner.get_all_tasks()
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; if it recurs, add the next occurrence to the same pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.owner.get_pet(task.pet_name).add_task(next_task)
        return next_task

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each pair of open tasks whose time ranges overlap."""
        open_tasks = self.sort_by_time(self.filter_tasks(completed=False))
        warnings = []
        for i, first in enumerate(open_tasks):
            for second in open_tasks[i + 1 :]:
                if first.due_date != second.due_date:
                    continue
                first_end = first.start_minutes() + first.duration_minutes
                if second.start_minutes() < first_end:
                    warnings.append(
                        f"Conflict on {first.due_date}: {first.description} ({first.pet_name}, "
                        f"{first.time} for {first.duration_minutes} min) overlaps "
                        f"{second.description} ({second.pet_name}, {second.time})"
                    )
        return warnings

    def next_available_slot(
        self, day: date, duration_minutes: int, day_start: str = "08:00", day_end: str = "20:00"
    ) -> Optional[str]:
        """Earliest HH:MM on a day where a task of this length fits between open tasks."""
        busy = sorted(
            (t.start_minutes(), t.start_minutes() + t.duration_minutes)
            for t in self.filter_tasks(completed=False)
            if t.due_date == day
        )
        h, m = day_start.split(":")
        cursor = int(h) * 60 + int(m)
        h, m = day_end.split(":")
        limit = int(h) * 60 + int(m)
        for start, end in busy:
            if cursor + duration_minutes <= start:
                break
            cursor = max(cursor, end)
        if cursor + duration_minutes > limit:
            return None
        return f"{cursor // 60:02d}:{cursor % 60:02d}"
