# Log Generator Simulator

Lightweight local tool that generates synthetic log files. Includes a small Flask backend and a responsive dark-themed web UI to generate, inspect, search, download and delete generated log files. All file operations are restricted to a configurable output folder (default: `generated_logs`).

---

## Application description
The application creates simulated log files for testing, demos, or load experiments. Features:
- Bulk generation of files with configurable lines-per-file and concurrency.
- Real-time progress monitoring and generation statistics (total / average / min / max durations).
- List, search, preview (bounded), download and delete files within the output directory.

## Algorithm (summary)
- write_one_file(index, lines): create a timestamped file and write sequential lines containing a timestamp and a message.
- worker_create_files(num, lines, concurrency): use ThreadPoolExecutor to run multiple file-write tasks in parallel.
- Each task returns its execution time (ms); the backend updates shared status protected by a `threading.Lock`.
- The frontend polls `/api/status` once per second to update the UI.

## User interface (UI)
- Single-page responsive UI (HTML / CSS / vanilla JS).
- Dark theme by default with a toggle to switch to light theme.
- Controls: number of files, lines per file, concurrency, and Start button.
- Status panel: started / ended timestamps, requested, created and in-progress counters.
- File list: View (preview up to configured characters), Download, Delete (with confirmation).
- Search: filename substring search (case-insensitive).

## README contents
- Overview
- Algorithm
- UI
- Project layout
- Installation & running
- Usage
- API reference
- Configuration
- Security notes & troubleshooting

## Project layout (repository)
```
.
├─ .venv/                      # optional venv (do not commit)
├─ generated_logs/             # output (created at runtime)
├─ static/
│  ├─ script.js                # frontend JS
│  └─ style.css                # CSS theme and layout
├─ templates/
│  └─ index.html               # single-page UI
├─ app.py                      # Flask backend, APIs, worker
├─ run.bat                     # Windows launcher (double-click)
├─ run.sh                      # macOS/Linux launcher
├─ README.md                   # this file
├─ requirements.txt            # pinned deps
└─ .gitpod.yml/.replit         # optional: cloud IDE auto-run configs
```

## Installation (local, Windows)
1. Clone repo:
   ```
   git clone <repo-url>
   cd log_simulator
   ```
2. Quick start (Windows): double‑click `run.bat` (creates venv if missing, installs deps, starts server).
   Or manually (PowerShell):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python app.py --host=127.0.0.1 --port=5000
   ```
3. Open browser: http://127.0.0.1:5000

macOS / Linux:
- Make `run.sh` executable: `chmod +x run.sh` then `./run.sh` or do similarly with venv and pip.

## Live demo / cloud IDE
- Gitpod (auto-install & run):  
  https://gitpod.io/#https://github.com/OWNER/REPO  (replace OWNER/REPO)
- Replit (import & run):  
  https://replit.com/github/OWNER/REPO  (replace OWNER/REPO)
- GitHub Codespaces:  
  https://github.com/codespaces/new?repo=OWNER/REPO

> Note: replace `OWNER/REPO` with the actual repo path before making public.

## Quick usage
- Enter: Number of files, Lines per file, Concurrency → Start Generate.
- Wait for Status to update; recent files will appear.
- Select a subdirectory from the dropdown → Apply → List files.
- View/Download/Delete files as needed; use Search to filter names.

## API (summary)
- GET / — UI
- POST /api/generate — { num_files, lines_per_file, concurrency }
- GET /api/status
- GET /api/list_dirs
- POST /api/set_view_dir — { dir }
- GET /api/list_files
- GET /api/search?q=...
- GET /api/file_content?filename=...
- POST /api/delete_file — { filename }
- GET /download/<filename>

## Configuration
- `GENERATED_DIR` in `app.py` — base output folder.
- `MAX_FILE_PREVIEW_CHARS` — preview limit (default 20000).
- app.py accepts CLI flags: `--host`, `--port`, `--debug`.

## Security & Notes
- All file operations are confined to `generated_logs/` — prevents path traversal.
- File deletion is permanent; UI has confirm but backup if needed.
- Flask dev server is for local/dev use only; use Waitress/Gunicorn for production.

## Quick troubleshooting
- Module not found: activate venv, `pip install -r requirements.txt`.
- Port in use: change `--port` when running.
- Files not showing: check if `view_dir` has been correctly applied to the subdirectory.

---

name: Run run.bat (smoke test)

on:
  workflow_dispatch:
  push:
    branches: [ main ]

jobs:
  run-bat-windows:
    runs-on: windows-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Start run.bat (background), wait and stop
        shell: powershell
        run: |
          # Start run.bat (it creates/uses .venv and starts app)
          Start-Process -FilePath "$PWD\run.bat" -NoNewWindow
          Write-Host "Waiting 15s for the app to start..."
          Start-Sleep -Seconds 15
          Write-Host "Stopping python processes (cleanup)..."
          Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
          Write-Host "Done"




