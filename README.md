# Log Generator Simulator

Lightweight local tool to generate synthetic log files for testing, demos, and load experiments. Provides a small Flask backend and a responsive dark-themed web UI to generate, inspect, search, download and delete generated log files. All file operations are restricted to a configurable output folder (default: `generated_logs`).

Status: Stable · Local-only · Minimal dependencies

## Features
- Bulk generation of timestamped log files with configurable lines-per-file and concurrency.
- Background generation using a thread pool; web UI polls status in real time.
- View (bounded preview), download, search (case-insensitive), and delete files.
- Directory selector limited to `generated_logs` and its subfolders.
- Dark/light theme and responsive UI.
- Safe path handling to prevent directory traversal.

## Quick links
- Demo (local): http://127.0.0.1:5000
- Gitpod / Replit / Codespaces: replace `OWNER/REPO` and use:
  - Gitpod: `https://gitpod.io/#https://github.com/OWNER/REPO`
  - Replit: `https://replit.com/github/OWNER/REPO`
  - Codespaces: `https://github.com/codespaces/new?repo=OWNER/REPO`

## Quickstart (Windows)
1. Clone repo:
   ```
   git clone <repo-url>
   cd log_simulator
   ```
2. Double-click `run.bat` (creates/activates venv, installs deps, starts server)
   - Or from PowerShell:
     ```
     .\.venv\Scripts\Activate.ps1
     python -m pip install -r requirements.txt
     python app.py
     ```
3. Open http://127.0.0.1:5000

## Quickstart (macOS / Linux)
1. Clone repo and enter folder:
   ```
   git clone <repo-url>
   cd log_simulator
   ```
2. Make launcher executable and run:
   ```
   chmod +x run.sh
   ./run.sh
   ```
   - Or manual:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     python -m pip install -r requirements.txt
     python app.py
     ```
3. Open http://127.0.0.1:5000

## One-click runner files
- `run.bat` — Windows launcher (double-click to run).
- `run.sh` — macOS / Linux launcher.
- `.gitpod.yml`, `.replit` — optional cloud IDE auto-run configuration.

## Usage (web UI)
- Controls: set Number of files, Lines per file, Concurrency → Start Generate.
- Monitor: started/ended timestamps, created/in-progress counters, aggregates.
- Directory selector: choose a `generated_logs` subfolder → Apply → List files.
- Actions per file: View (preview up to 20k chars), Download, Delete (confirm).
- Search: filename substring (case-insensitive).

## API (high level)
- GET / — UI
- POST /api/generate — start generation; JSON: { num_files, lines_per_file, concurrency }
- GET /api/status — current status and recent files
- GET /api/list_dirs — allowed view directories
- POST /api/set_view_dir — set view directory; JSON: { dir }
- GET /api/list_files — list files in current view directory
- GET /api/search?q=... — filename substring search
- GET /api/file_content?filename=... — bounded file content (configurable)
- POST /api/delete_file — delete file; JSON: { filename }
- GET /download/<filename> — download file

## Configuration
- Change `GENERATED_DIR` in `app.py` to modify the output folder.
- `MAX_FILE_PREVIEW_CHARS` controls preview size (default 20000).
- `app.py` accepts `--host`, `--port`, and `--debug` CLI flags.

## Project layout
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
├─ run.bat                     # Windows launcher
├─ run.sh                      # macOS/Linux launcher
├─ README.md                   # this file
├─ requirements.txt            # pinned deps
└─ .gitpod.yml/.replit         # optional: cloud IDE auto-run configs
```

## Development notes
- Shared state is protected by `threading.Lock`.
- Long-running generation runs in background threads; Flask dev server is for local use only.
- Use safe path joining (`safe_join_base`) to avoid directory traversal.

## CI & Deployment
- Example production servers:
  - Waitress (Windows): `waitress-serve --port=5000 app:app`
  - Gunicorn (Linux): `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
- Add a GitHub Actions workflow to run lint/tests before merging.

## Contributing
- Use feature branches and open pull requests.
- Add tests for path-safety and API behavior (use temporary directories).
- Provide a `CONTRIBUTING.md` for development conventions.

## Recommended .gitignore
```
.venv/
__pycache__/
generated_logs/
*.pyc
.env
```

## License
Add a `LICENSE` file (MIT recommended) before publishing.

---

Checklist before publishing
- [ ] Add LICENSE
- [ ] Pin dependencies in `requirements.txt`
- [ ] Add `.gitignore`
- [ ] Add `run.bat` and `run.sh` (already included)
- [ ] Add screenshot in `assets/` for README header


