# Log Generator Simulator

Lightweight local tool to generate synthetic log files for testing, demos, or load experiments. Provides a small Flask backend and a responsive, dark-themed web UI to generate, inspect, search, download and delete generated log files. Designed to be safe for local use — all file operations are restricted to a configurable output folder.

---

Status: Stable · Local-only · Minimal dependencies

Table of contents
- Features
- Demo
- Quickstart (Windows)
- Quickstart (Linux / macOS)
- One‑click cloud IDEs (Gitpod / Replit / Codespaces)
- Usage
- API reference
- Project layout
- Configuration
- Development notes
- CI & Deployment
- Contributing
- License

Features
- Generate many timestamped log files concurrently with configurable lines-per-file and concurrency.
- Background generation with a thread pool; UI polls status in real time.
- List, view (bounded to 20k chars), download and delete files from a selected output directory (restricted to `generated_logs`).
- Case-insensitive filename search.
- Dark/light theme toggle and responsive layout.
- Safe path handling to prevent directory traversal.

Demo
- Open http://127.0.0.1:5000 after starting the app.
- UI includes controls for: number of files, lines per file, concurrency, directory selector, search, and file viewer.

Quickstart (Windows, recommended)
1. Clone repository:
   ```
   git clone <repo-url>
   cd log_simulator
   ```
2. Create and activate virtual environment (PowerShell):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. Run:
   ```
   python app.py
   ```
5. Open browser: http://127.0.0.1:5000

Quickstart (Linux / macOS)
1. Clone and enter repo:
   ```
   git clone <repo-url>
   cd log_simulator
   ```
2. Create & activate venv:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install:
   ```
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. Run:
   ```
   python app.py
   ```
5. Open http://127.0.0.1:5000

One‑click cloud IDEs (Gitpod / Replit / Codespaces)
- Gitpod: replace OWNER/REPO and open:
  https://gitpod.io/#https://github.com/OWNER/REPO
- Replit: replace OWNER/REPO and open:
  https://replit.com/github/OWNER/REPO
- Codespaces: open in a new Codespace:
  https://github.com/codespaces/new?repo=OWNER/REPO

(Include `.gitpod.yml` and `.replit` in repo to auto-install and run on these services.)

Usage
- Controls: set Number of files, Lines per file, Concurrency → click "Start Generate".
- Monitor the Status panel for started/ended timestamps, created and in-progress counters.
- Use the directory dropdown to choose which subfolder of `generated_logs/` to inspect; click Apply.
- Use View to display file content (up to 20k chars), Download to save, or Delete (with confirmation) to remove permanently.
- Search filters filenames by substring (case-insensitive).

API reference (high level)
- GET / — UI
- POST /api/generate — start generation; JSON: { num_files, lines_per_file, concurrency }
- GET /api/status — current status and recent files
- GET /api/list_dirs — allowed view directories
- POST /api/set_view_dir — set view directory; JSON: { dir }
- GET /api/list_files — list files in current view directory
- GET /api/search?q=... — filename substring search
- GET /api/file_content?filename=... — bounded file content
- POST /api/delete_file — delete file; JSON: { filename }
- GET /download/<filename> — download file

Project layout
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
├─ README.md                   # this file
├─ requirements.txt            # pinned deps
└─ .gitpod.yml/.replit         # optional: cloud IDE auto-run configs
```

Configuration
- Edit `GENERATED_DIR` in `app.py` to change the base output folder.
- `write_one_file()` controls file content and format; modify for custom log formats.
- File view limit: default 20,000 characters — change in `api_file_content` if needed.
- To bind to all interfaces (useful in cloud IDEs), run:
  ```
  python app.py --host=0.0.0.0
  ```
  or set the HOST env var and update `app.run()` accordingly.

Development notes
- Shared status is protected by a `threading.Lock` to avoid races.
- Long-running tasks run in background threads; the Flask dev server is for local use only. For production, use a WSGI server and add authentication.
- The app enforces safe path joining to prevent directory traversal.

CI & Deployment
- Example GitHub Actions workflow (add `.github/workflows/python-app.yml`) to run lint/tests and optionally start a simple server for smoke tests:
  - Use Python 3.10+ runner
  - Install dependencies from `requirements.txt`
  - Run unit tests (if added)
- Production serving options:
  - Waitress (Windows): `waitress-serve --port=5000 app:app`
  - Gunicorn (Linux): `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
- `requirements.txt` included for reproducible installs.

Recommended .gitignore
```
.venv/
__pycache__/
generated_logs/
*.pyc
.env
```

Contributing
- Keep changes small and documented.
- Add tests for path-safety and API behavior using temporary directories.
- Use feature branches and open pull requests.
- Add a `CONTRIBUTING.md` describing local dev steps and testing.

Optional assets for a polished GitHub repo
- Add `assets/screenshot.png` or a short GIF and reference it at the top of this README.
- Include `LICENSE` (MIT recommended for simplicity).
- Provide a `CHANGELOG.md` for important updates.

License
- Add your preferred license file (e.g., MIT). If none provided, treat the project as unlicensed.

Contact / Issues
- Open issues on the GitHub repository for bugs or feature requests.

---

Small checklist before publishing to GitHub
- [ ] Add LICENSE
- [ ] Add `requirements.txt` (pinned versions)
- [ ] Add `.gitignore`
- [ ] Add `.gitpod.yml` and/or `.replit` if you want one-click runs
- [ ] Add a screenshot in `assets/` and reference it at top of README


