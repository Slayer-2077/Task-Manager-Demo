# Focus Task Manager

Focus is a lightweight daily task manager built with FastAPI. Users can create an account, sign in, and manage their own task list from a simple browser interface.

## Features

- User registration and login
- Session-based authentication
- Create, view, update, and delete tasks
- Mark tasks as completed
- Per-user task isolation
- Responsive HTML/CSS interface
- Async SQLite persistence through SQLAlchemy and `aiosqlite`

## Tech stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy asyncio
- SQLite
- Jinja2 templates
- Vanilla JavaScript and CSS

## Getting started

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the development server

Run this command from the project root:

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login) in your browser.

The application creates its database tables automatically on startup. Local SQLite data is stored in `test.db` and is excluded from version control.

## Application routes

| Method | Route | Description |
| --- | --- | --- |
| GET | `/login` | Display the sign-in page |
| POST | `/login` | Authenticate a user |
| GET | `/register` | Display the registration page |
| POST | `/register` | Create an account |
| GET | `/task-manager` | Display the task manager |
| GET | `/tasks` | List the signed-in user's tasks |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

FastAPI's generated API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) while the server is running.

## Project structure

```text
Task-Manager-Demo/
├── app/
│   ├── db.py          # Async database engine and sessions
│   ├── main.py        # FastAPI application and routes
│   └── models.py      # User and task models
├── static/
│   ├── index.html     # Login page
│   ├── register.html  # Registration page
│   ├── tasks.html     # Task manager page
│   └── style.css      # Application styles
├── requirements.txt
└── README.md
```

## Development notes

This project is configured for local development. Before deploying it publicly, configure a strong secret key, hash passwords instead of storing them directly, add production-grade validation and error handling, and use a production database configuration.
