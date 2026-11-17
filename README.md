# ALGO DNA

#### Video Demo: https://youtu.be/UXdP4L0CPZw

#### GitHub Repository: https://github.com/SifatNycto/algodna

## Description

ALGO DNA is a web-based programming practice tracker designed for competitive programmers who want to understand their problem-solving habits and improve through consistent practice.

When preparing for programming contests, simply counting the number of problems solved does not provide a complete picture of a programmer's progress. It is also important to understand which topics are difficult, how frequently problems require multiple attempts, and where additional practice is needed. ALGO DNA addresses this by allowing users to record their problem-solving activities and transform those records into a personal learning profile.

The main idea behind ALGO DNA is to connect practice tracking with performance analysis. Users can record problems along with their platform, topic, difficulty, result, number of attempts, wrong attempts, practice date, and optional notes. The application analyzes these records to generate useful performance summaries and identify topics that may require more attention. Instead of providing the same study plan to everyone, ALGO DNA generates practice suggestions based on each user's recorded activity.

## Features

### 1. User Authentication

ALGO DNA provides user registration, login, and logout functionality. Passwords are stored as securely generated password hashes rather than plain text. Each practice record is associated with the account that created it, ensuring that users see their own practice history and performance information. Routes containing personal practice data require an authenticated session.

### 2. Practice Logging

The Log Practice page allows users to record their programming activities. Each entry includes the problem name, programming platform, topic, difficulty level, result, total attempts, wrong attempts, practice date, and optional notes.

The application validates required fields and checks whether attempt counts are valid before saving a record. This helps maintain consistent data for the performance analysis.

### 3. Dashboard

The Dashboard provides a quick overview of a user's programming practice. It displays the total number of recorded problems, solved and attempted counts, success rate, recent activity, and priority topics.

The purpose of the dashboard is to make progress easier to understand and help users identify what they should focus on next.

### 4. Performance Insights

The Insights page analyzes practice records by topic and difficulty. It calculates topic-based solve rates and considers wrong attempts when estimating which topics may require more attention. It also provides performance summaries for different difficulty levels.

These insights help users recognize their strengths and weaknesses instead of relying only on the total number of problems they have solved.

### 5. Personalized Practice Roadmap

The My Roadmap page generates practice suggestions using the user's recorded performance. Topics are ranked according to their solve rates, activity volume, and wrong-attempt patterns.

For example, a topic with very little recorded activity may receive a foundation-building recommendation. A topic with a low solve rate may receive suggestions to review its core concepts and practise with guided and independent problems. This makes the roadmap responsive to the user's progress.

## Technologies Used

- **Python:** Main programming language used for application logic.
- **Flask:** Web framework responsible for routing, sessions, form handling, and page rendering.
- **SQLite:** Lightweight relational database for storing user accounts and practice records.
- **HTML:** Structure of the application's web pages.
- **CSS:** Styling and visual presentation of the user interface.
- **Jinja:** Template engine used to render dynamic content.

## Implementation and Design Choices

The application is built using Python and Flask. Flask handles application routes, form submissions, authentication sessions, and rendering the HTML templates. SQLite was selected as the database because it is lightweight and does not require a separate database server, making it suitable for a small educational web application.

The database contains two main tables: `users` and `attempts`. The users table stores account information, while the attempts table stores practice records and connects each record to its owner through a foreign key. Parameterized SQL queries are used when interacting with the database. Password hashing and verification are handled using Werkzeug's security utilities.

One important design decision was to generate practice recommendations from each user's actual records instead of displaying a fixed roadmap. The recommendation system uses understandable, rule-based logic based on topic performance, problem-solving activity, and wrong attempts. It does not claim to use machine learning or predict a user's future performance. This approach keeps the system simple, transparent, and relevant to its main purpose.

## Project Files

The project is organized into the following files and directories:

- **`app.py`** — The main Flask application. It initializes the database, handles user registration and login, protects authenticated routes, saves and deletes practice records, calculates performance analytics, and generates roadmap suggestions.
- **`requirements.txt`** — Contains the Python dependencies required to run the application.
- **`static/styles.css`** — Contains the CSS rules used to style the application's interface and page components.
- **`templates/layout.html`** — Defines the shared HTML layout used by the other pages.
- **`templates/register.html`** — Contains the user registration interface.
- **`templates/login.html`** — Contains the login interface.
- **`templates/dashboard.html`** — Displays the user's practice statistics, recent activity, and priority topics.
- **`templates/log.html`** — Provides the form for recording programming practice sessions.
- **`templates/insights.html`** — Displays topic-based and difficulty-based performance analysis.
- **`templates/roadmap.html`** — Displays practice recommendations generated from the user's recorded activity.

The SQLite database file, `algodna.db`, is initialized automatically by the application. It does not need to be created manually.

## How to Run the Project

To run ALGO DNA locally, Python must be installed on your computer.

First, open a terminal in the project directory and create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask development server:

```bash
flask --app app run --debug
```

Open the local address printed in the terminal, usually `http://127.0.0.1:5000`, in your web browser.

Register an account, log some programming practice sessions, and explore the Dashboard, Insights, and My Roadmap pages.

## Limitations and Future Improvements

ALGO DNA is an academic learning project and is not intended to be a production-ready service. It currently uses a local SQLite database and a rule-based recommendation system. Before deploying the application publicly, the default Flask `SECRET_KEY` must be replaced with a secure environment-based value.

Possible future improvements include graphical progress visualizations, practice-history filtering, data export, integration with competitive programming platforms, and more flexible roadmap recommendations.

## Acknowledgment

ALGO DNA was developed as my CS50x Final Project. AI-based tools were used as development assistance during parts of the project. The implementation and design decisions should be understood and reviewed by the developer, with AI assistance disclosed in the relevant source-code comments in accordance with CS50x final project guidelines.