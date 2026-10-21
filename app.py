from datetime import date, time
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = Path("data.json")
PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Streamlit reruns this script on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(DATA_FILE) if DATA_FILE.exists() else Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def save() -> None:
    owner.save_to_json(DATA_FILE)


owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and pet_name.strip():
        if owner.get_pet(pet_name.strip()):
            st.warning(f"{pet_name} already exists.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            save()
            st.success(f"Added {pet_name}.")

st.subheader("Schedule a task")
if not owner.pets:
    st.info("Add a pet first.")
else:
    with st.form("add_task", clear_on_submit=False):
        target = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        c1, c2, c3 = st.columns(3)
        when = c1.time_input("Time", value=time(8, 0))
        duration = c2.number_input("Minutes", min_value=1, max_value=240, value=20)
        priority = c3.selectbox("Priority", ["high", "medium", "low"])
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        due = st.date_input("Date", value=date.today())
        if st.form_submit_button("Add task") and description.strip():
            owner.get_pet(target).add_task(
                Task(description.strip(), when.strftime("%H:%M"), due, frequency, priority, int(duration))
            )
            save()
            st.success(f"Scheduled '{description}' for {target}.")

st.divider()
st.subheader("Schedule")

for warning in scheduler.detect_conflicts():
    st.warning(f"⚠️ {warning}")

f1, f2, f3 = st.columns(3)
pet_filter = f1.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
status_filter = f2.selectbox("Status", ["All", "Open", "Done"])
order = f3.selectbox("Order", ["By time", "By priority"])

tasks = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "Open": False, "Done": True}[status_filter],
)
tasks = scheduler.sort_by_time(tasks) if order == "By time" else scheduler.sort_by_priority(tasks)

if not tasks:
    st.info("No tasks match.")
for i, task in enumerate(tasks):
    cols = st.columns([5, 2])
    mark = "✅" if task.completed else "⏳"
    cols[0].write(
        f"{mark} **{task.due_date} {task.time}** · {task.pet_name} · {task.description} "
        f"({task.duration_minutes} min, {PRIORITY_ICON[task.priority]}, {task.frequency})"
    )
    if not task.completed and cols[1].button("Mark done", key=f"done_{i}_{id(task)}"):
        nxt = scheduler.mark_task_complete(task)
        save()
        if nxt:
            st.toast(f"Next {task.description} scheduled for {nxt.due_date}")
        st.rerun()

st.divider()
st.subheader("Find a free slot")
slot_minutes = st.number_input("Task length (minutes)", min_value=1, max_value=240, value=30)
if st.button("Next available slot today"):
    slot = scheduler.next_available_slot(date.today(), int(slot_minutes))
    if slot:
        st.success(f"Next free {slot_minutes} minute slot today: {slot}")
    else:
        st.error("No free slot left today between 08:00 and 20:00.")
