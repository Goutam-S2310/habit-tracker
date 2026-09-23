import sqlite3
from datetime import date, timedelta
import streamlit as st
import pandas as pd

DB_NAME = "habits.db"

st.set_page_config(
    page_title="Habit Tracker",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Database ----------
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT DEFAULT '✓',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_date TEXT NOT NULL,
            UNIQUE(habit_id, completed_date),
            FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    return conn

conn = get_connection()

# ---------- Data helpers ----------
def get_habits():
    return pd.read_sql_query(
        "SELECT id, name, icon FROM habits ORDER BY id",
        conn
    )

def get_completed_dates(habit_id):
    rows = conn.execute(
        "SELECT completed_date FROM completions WHERE habit_id = ?",
        (habit_id,)
    ).fetchall()
    return {date.fromisoformat(row[0]) for row in rows}

def is_completed(habit_id, day):
    row = conn.execute(
        "SELECT 1 FROM completions WHERE habit_id = ? AND completed_date = ?",
        (habit_id, day.isoformat())
    ).fetchone()
    return row is not None

def set_completion(habit_id, day, completed):
    if completed:
        conn.execute(
            "INSERT OR IGNORE INTO completions (habit_id, completed_date) VALUES (?, ?)",
            (habit_id, day.isoformat())
        )
    else:
        conn.execute(
            "DELETE FROM completions WHERE habit_id = ? AND completed_date = ?",
            (habit_id, day.isoformat())
        )
    conn.commit()

def calculate_streak(habit_id):
    completed = get_completed_dates(habit_id)
    if not completed:
        return 0

    today = date.today()

    # A streak can be current if completed today OR yesterday.
    if today not in completed and today - timedelta(days=1) not in completed:
        return 0

    cursor = today if today in completed else today - timedelta(days=1)
    streak = 0

    while cursor in completed:
        streak += 1
        cursor -= timedelta(days=1)

    return streak

def delete_habit(habit_id):
    conn.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f7fbf5 0%, #ffffff 55%, #f1f8ef 100%);
    }

    .hero {
        padding: 28px 8px 18px;
        text-align: center;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 4px;
        color: #1f3322;
        letter-spacing: -1px;
    }

    .hero p {
        color: #657565;
        font-size: 17px;
        margin-top: 0;
    }

    .stat-card {
        background: white;
        border: 1px solid #e2eadf;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 5px 18px rgba(39, 75, 40, 0.06);
    }

    .stat-label {
        color: #718071;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .stat-value {
        color: #25442a;
        font-size: 29px;
        font-weight: 700;
        margin-top: 4px;
    }

    .habit-card {
        background: white;
        border: 1px solid #e2eadf;
        border-radius: 18px;
        padding: 17px 18px;
        margin-bottom: 12px;
        box-shadow: 0 5px 18px rgba(39, 75, 40, 0.05);
    }

    .habit-name {
        font-size: 18px;
        font-weight: 650;
        color: #27352a;
    }

    .streak {
        color: #df6d2e;
        font-weight: 700;
        font-size: 14px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        color: #263b29;
        margin: 20px 0 10px;
    }

    .day-box {
        text-align: center;
        padding: 6px 2px;
        border-radius: 10px;
        font-size: 11px;
        border: 1px solid #e0e9dc;
    }

    .day-done {
        background: #69b978;
        color: white;
        border-color: #69b978;
    }

    .day-empty {
        background: #f2f6f0;
        color: #748274;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
    }

    .footer {
        text-align: center;
        color: #7b887b;
        font-size: 13px;
        padding: 30px 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>🌿 Habit Tracker</h1>
    <p>Build better routines, one day at a time.</p>
</div>
""", unsafe_allow_html=True)

habits = get_habits()
today = date.today()

# ---------- Add habit ----------
with st.expander("＋ Add a new habit", expanded=False):
    with st.form("add_habit_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 5, 1])
        with c1:
            icon = st.selectbox("Icon", ["💧", "📖", "🏋️", "💻", "🧘", "🏃", "🎯", "🧠", "🎵", "✓"])
        with c2:
            name = st.text_input("Habit name", placeholder="e.g. Drink 2L water")
        with c3:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("Add", use_container_width=True)

        if submitted:
            if not name.strip():
                st.warning("Please enter a habit name.")
            else:
                conn.execute(
                    "INSERT INTO habits (name, icon, created_at) VALUES (?, ?, ?)",
                    (name.strip(), icon, today.isoformat())
                )
                conn.commit()
                st.success(f'Added "{name.strip()}"')
                st.rerun()

# ---------- Summary ----------
habits = get_habits()
total_habits = len(habits)
completed_today = sum(is_completed(int(row.id), today) for row in habits.itertuples())
completion_rate = round((completed_today / total_habits) * 100) if total_habits else 0
best_current_streak = max(
    (calculate_streak(int(row.id)) for row in habits.itertuples()),
    default=0
)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Today</div><div class="stat-value">{completed_today}/{total_habits}</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Completion</div><div class="stat-value">{completion_rate}%</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Best Current Streak</div><div class="stat-value">🔥 {best_current_streak}</div></div>', unsafe_allow_html=True)

# ---------- Habits ----------
st.markdown('<div class="section-title">My Habits</div>', unsafe_allow_html=True)

if habits.empty:
    st.info("No habits yet. Click “Add a new habit” to create your first one.")
else:
    for row in habits.itertuples():
        habit_id = int(row.id)
        done_today = is_completed(habit_id, today)
        streak = calculate_streak(habit_id)

        with st.container(border=True):
            left, middle, right = st.columns([4.7, 1.5, 1.1])

            with left:
                st.markdown(
                    f'<div class="habit-name">{row.icon} &nbsp; {row.name}</div>'
                    f'<div class="streak">🔥 {streak} day{"s" if streak != 1 else ""} streak</div>',
                    unsafe_allow_html=True
                )

            with middle:
                if st.button(
                    "✓ Completed" if done_today else "Mark done",
                    key=f"complete_{habit_id}",
                    use_container_width=True,
                    type="primary" if done_today else "secondary",
                ):
                    set_completion(habit_id, today, not done_today)
                    st.rerun()

            with right:
                if st.button("Delete", key=f"delete_{habit_id}", use_container_width=True):
                    delete_habit(habit_id)
                    st.rerun()

# ---------- 7-day view ----------
st.markdown('<div class="section-title">Last 7 Days</div>', unsafe_allow_html=True)

days = [today - timedelta(days=i) for i in range(6, -1, -1)]

if habits.empty:
    st.caption("Your weekly progress will appear here after you add habits.")
else:
    for row in habits.itertuples():
        habit_id = int(row.id)
        cols = st.columns(8)
        with cols[0]:
            st.markdown(f"**{row.icon} {row.name}**")
        for i, day in enumerate(days, start=1):
            with cols[i]:
                done = is_completed(habit_id, day)
                label = day.strftime("%a")
                symbol = "✓" if done else "·"
                cls = "day-done" if done else "day-empty"
                st.markdown(
                    f'<div class="day-box {cls}"><b>{label}</b><br>{symbol}</div>',
                    unsafe_allow_html=True
                )

# ---------- Progress chart ----------
if not habits.empty:
    st.markdown('<div class="section-title">Weekly Progress</div>', unsafe_allow_html=True)

    chart_data = []
    for day in days:
        completed = sum(is_completed(int(row.id), day) for row in habits.itertuples())
        chart_data.append({
            "Day": day.strftime("%a"),
            "Completed": completed
        })

    chart_df = pd.DataFrame(chart_data).set_index("Day")
    st.bar_chart(chart_df, height=250)

st.markdown(
    '<div class="footer">Local-first habit tracking • Data is stored in SQLite on this device.</div>',
    unsafe_allow_html=True
)
