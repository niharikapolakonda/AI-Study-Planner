import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Planner")
st.write("Your personal assistant for smarter studying.")

st.sidebar.header("⚙️ Plan Your Studies")

student = st.sidebar.text_input(
    "Your name", placeholder="Enter your name"
)

subject_text = st.sidebar.text_input(
    "Subjects (separate with commas)",
    value="Python, DBMS, Computer Networks, DAA"
)

daily_hours = st.sidebar.slider(
    "Study hours per day", 1, 8, 3
)

plan_days = st.sidebar.slider(
    "Create a plan for how many days?", 1, 14, 7
)

exam_date = st.sidebar.date_input(
    "Next exam date",
    value=date.today() + timedelta(days=7),
    min_value=date.today()
)

subjects = list(dict.fromkeys(
    s.strip() for s in subject_text.split(",") if s.strip()
))

difficult = st.sidebar.multiselect(
    "Subjects you find difficult",
    options=subjects
)

st.subheader("👋 Welcome to your study dashboard")
st.write(
    f"Hello, {student or 'Student'}! "
    "Let's make your study time productive."
)

days_until_exam = max(1, (exam_date - date.today()).days)

st.info(
    f"Your next exam is in {days_until_exam} day(s). "
    f"You have planned {daily_hours} study hour(s) per day."
)

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "plan_id" not in st.session_state:
    st.session_state.plan_id = 0

if st.button("✨ Generate My Smart Study Plan",
             type="primary"):

    if not subjects:
        st.error("Please enter at least one subject.")
    else:
        priorities = {}

        for subject in subjects:
            score = 1.0

            # Give extra priority to difficult subjects
            if subject in difficult:
                score += 2.0

            # Increase urgency as the exam approaches
            score += 7 / days_until_exam

            priorities[subject] = score

        allocated = {subject: 0 for subject in subjects}
        tasks = []

        # Divide study time into 30-minute sessions
        sessions_per_day = daily_hours * 2

        for day_number in range(plan_days):
            study_date = date.today() + timedelta(
                days=day_number
            )

            for _ in range(sessions_per_day):
                # Prefer subjects receiving less time
                # relative to their priority
                subject = min(
                    subjects,
                    key=lambda s: (
                        allocated[s] / priorities[s],
                        subjects.index(s)
                    )
                )

                allocated[subject] += 1

                tasks.append({
                    "Date": study_date.isoformat(),
                    "Time": "30-minute study session",
                    "Subject": subject,
                    "Task": (
                        f"Study {subject}, then revise "
                        "your notes or solve practice questions"
                    )
                })

        st.session_state.tasks = tasks
        st.session_state.plan_id += 1

        st.success("Your smart study plan is ready!")

if st.session_state.tasks:
    tasks = st.session_state.tasks

    st.subheader("📅 Your Study Timetable")

    completed = 0
    total = len(tasks)

    for i, task in enumerate(tasks):
        col1, col2 = st.columns([0.12, 0.88])

        with col1:
            is_done = st.checkbox(
                "Done",
                key=f"done_{st.session_state.plan_id}_{i}"
            )

        with col2:
            st.write(
                f"**{task['Date']} | {task['Subject']}**"
            )
            st.caption(task["Task"])

        if is_done:
            completed += 1

    progress = completed / total if total else 0

    st.subheader("📈 Your Progress")

    st.progress(progress)
    st.write(
        f"Completed {completed} out of {total} sessions "
        f"({progress:.0%})"
    )

    if completed == total:
        st.balloons()
        st.success("Excellent! You completed your study plan.")

    df = pd.DataFrame(tasks)

    st.download_button(
        "⬇️ Download Study Plan as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="my_study_plan.csv",
        mime="text/csv"
    )

    st.subheader("📊 Subject-wise Study Time")

    summary = df["Subject"].value_counts().reset_index()
    summary.columns = ["Subject", "Sessions"]

    summary["Study Hours"] = summary["Sessions"] * 0.5

    st.bar_chart(
        summary.set_index("Subject")["Study Hours"]
    )

else:
    st.write(
        "Enter your details in the sidebar and click "
        "'Generate My Smart Study Plan' to begin."
    )

st.divider()
st.caption(
    "AI Study Planner | Student productivity project"
)