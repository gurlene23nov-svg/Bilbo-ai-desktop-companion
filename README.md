# Bilbo — AI Desktop Companion

Bilbo is a small Windows desktop companion with a floating rabbit, a local chat
window, saved conversation history, and read-only laptop status and storage
reports. It is built with Python, Tkinter/CustomTkinter, FastAPI, and SQLite.

[GitHub repository](https://github.com/gurlene23nov-svg/Bilbo-ai-desktop-companion)

> **Project status:** Bilbo is an actively developed personal project. The
> current Python workflow and the automated checks described below have been
> verified on Windows with Python 3.14.3. Other Python versions and packaged
> builds have not been verified.

## Features

- **Floating desktop pet:** a transparent, always-on-top rabbit window that can
  move around the desktop, be dragged, and open the chat when clicked.
- **Mood expressions:** the pet reads its mood from local state and selects an
  available mood image. Missing expressions fall back to the happy image.
- **Local companion chat:** a separate desktop chat window communicates with a
  FastAPI service bound to `127.0.0.1`.
- **Saved conversation history:** chat messages are stored in a local SQLite
  database and shown in chronological order with timestamps.
- **Laptop snapshots:** ask Bilbo about CPU, memory, the C: drive, battery
  availability, uptime, or overall laptop status.
- **Read-only storage reports:** review large files in Downloads and temporary
  file candidates. Bilbo does not delete files.
- **Basic security status checks:** on supported Windows systems, Bilbo makes
  read-only PowerShell checks for Windows Defender and Firewall status.
- **No external AI service required:** everyday replies and mood detection use
  local, rule-based responses; no cloud model or API key is configured.

## Screenshots

Screenshots are intentionally not included yet.

## Requirements

- Windows 10 or Windows 11.
- Python 3.14.3 is the version verified for this project; other Python versions
  have not yet been tested.
- Internet access only to install Python packages. Bilbo's backend listens on
  localhost and does not require an external AI service.

## Installation

Open PowerShell in the cloned repository:

```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell does not recognize `py -3.14`, install Python 3.14 and make sure
the Python Launcher is available, or create the environment with the full path
to your Python 3.14 executable.

## Launch Bilbo

Double-click `start_bilbo.bat`, or run it from the repository directory:

```powershell
.\start_bilbo.bat
```

The launcher starts the local API and the floating pet. Click Bilbo to open the
chat window. The backend creates `data\bilbo.db` on its first startup and keeps
conversation history on this computer.

### Optional: start Bilbo when you sign in

Windows startup registration is a per-user setting and is not enabled by
cloning this repository. To enable it yourself:

1. Press **Win+R**, enter `shell:startup`, and press **Enter**.
2. Create a shortcut in the opened Startup folder to this repository's
   `start_bilbo.bat`.
3. To disable startup later, remove that shortcut.

## Chat and API

The desktop client calls:

- `POST http://127.0.0.1:8000/api/chat`
- `GET http://127.0.0.1:8000/api/history`

The older `POST /chat` and `GET /history` routes remain available for
compatibility. The backend also serves its OpenAPI document at
`http://127.0.0.1:8000/docs` while it is running.

Example requests:

```json
{"message": "How is my laptop?"}
```

```json
{"message": "Show my conversation history"}
```

Chat commands and laptop replies are handled locally. The security checks
report what Windows makes available and do not disable protections or start a
malware scan. File cleanup is intentionally disabled; the legacy discard API
returns `501 Not Implemented` and does not change files.

Example questions include:

- "Hi Bilbo"
- "How is my laptop?"
- "Show my conversation history"
- "Check my laptop security"
- "Help me free up storage"
- "Find large files"
- "I'm feeling stressed"

## Data and privacy

- Conversations are stored locally in `data\bilbo.db`.
- Pet mood state and backend logs are local runtime files in `data\`.
- Do not upload the database, runtime logs, or personal state files.
- Storage reporting is informational. The scan examines Downloads and
  temporary-file candidates; inaccessible items may be skipped.
- Paths containing a directory named `gurlene` are excluded from storage
  scans, and storage scans do not follow symbolic links or Windows junctions.
  Bilbo's own project directory and selected personal folders are also
  protected.
- The backend binds to `127.0.0.1`; it is not configured for LAN or public
  access.

## Tests

Run the automated checks from the repository root:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests cover chat and history routes, database initialization and ordering,
intent priority, storage safety, and pet mood mapping. Windows security
providers and the visual desktop experience still require manual verification
on the target machine.

## Project layout

```text
backend/
  api/routes.py       Chat, history, laptop, security, and storage routes
  database.py         Local SQLite conversation history
  file_manager.py     Read-only storage reports and security checks
  main.py             FastAPI application entry point
  mood.py             Local mood detection and responses
  system_monitor.py   CPU, memory, disk, battery, and uptime snapshots
frontend/
  assets/             Rabbit artwork and mood sheet
  chat_window.py      Desktop chat interface
  companion.py        Floating desktop pet
tests/
  test_backend_audit.py
data/                 Local database, state, and logs (not for source control)
start_bilbo.bat       Windows development launcher
```

## Troubleshooting

- **The chat cannot connect:** start Bilbo with `start_bilbo.bat` and check
  whether another application is already using port `8000`.
- **The pet image is missing:** keep the `frontend\assets` directory alongside
  the source files.
- **The security report is unavailable:** Defender or Firewall PowerShell
  cmdlets may be missing or restricted on some Windows editions; Bilbo reports
  available information only.
- **Conversation history is private:** the database is local to this checkout.
  Do not share `data\bilbo.db` when reporting a problem.

## Contributing

Bug reports and focused contributions are welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md) for local setup, tests, and project safety
guidelines.

## License

No license has been selected for this repository yet. Until the project owner
adds one, reuse and redistribution permissions are not granted by this
repository.
