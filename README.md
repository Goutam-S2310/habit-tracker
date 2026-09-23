# 🌿 Habit Tracker

A simple, beginner-friendly habit tracking app built with **Python, Streamlit and SQLite**.

## Features

- Add custom daily habits
- Choose an emoji/icon for each habit
- Mark habits complete for today
- Automatic current streak calculation
- Last 7 days progress view
- Weekly completion chart
- Completion percentage
- Delete habits
- Local SQLite database — no external account required
- Responsive Streamlit interface

## Tech Stack

- **Python**
- **Streamlit**
- **SQLite**
- **Pandas**

## Project Structure

```text
habit-tracker-streamlit/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── config.toml
```

The SQLite database (`habits.db`) is created automatically when the app runs.

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/habit-tracker-streamlit.git
cd habit-tracker-streamlit
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
streamlit run app.py
```

Streamlit will open the app in your browser.

## GitHub Repository Description

> A beginner-friendly habit tracker built with Python, Streamlit and SQLite. Track daily habits, streaks and weekly progress with a clean interactive dashboard.

## Future Improvements

- Monthly calendar
- Habit reminders
- User accounts
- Dark mode
- Export progress to CSV
- Habit categories
- Achievement badges
- Cloud database support

## License

This project is open source and intended for learning and portfolio use.
