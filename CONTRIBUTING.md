# Contributing

Thanks for your interest in Bilbo. Contributions should keep the Windows
desktop experience, local conversation history, and read-only system tools
reliable.

## Set up locally

1. Install Python 3.14.3 on Windows.
2. Create and activate a virtual environment:

   ```powershell
   py -3.14 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Run Bilbo with `.\start_bilbo.bat`.

## Validate changes

From the repository root, run:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Add or update tests when behavior changes. Report Windows-only behavior that
you could not verify instead of assuming it works.

## Project guidelines

- Keep the backend bound to localhost unless a separately reviewed feature
  explicitly requires otherwise.
- Do not add automatic file deletion, Recycle Bin operations, or changes to
  Defender, Firewall, or other system settings.
- Exclude the Bilbo project, private runtime data, and every directory named
  `gurlene` from storage scans and cleanup operations.
- Do not commit databases, logs, pet state, credentials, local virtual
  environments, or personal conversation content.
- Prefer small, focused changes and preserve the existing Python desktop
  workflow.

## Reporting an issue

Include the Windows version, Python version, steps to reproduce, expected
behavior, and sanitized error output. Never attach `data\bilbo.db`, secrets,
personal file paths, or private conversations.
