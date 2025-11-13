# Log Generator Simulator

Lightweight local tool to generate synthetic log files for testing, demos, or load experiments. Provides a small Flask backend and a responsive, dark-themed web UI to generate, inspect, search, download and delete generated log files. Designed to be safe for local use — all file operations are restricted to a configurable output folder.

---

Status: Stable · Local-only · Minimal dependencies

Table of contents
- Features
- Demo
- Quickstart (Windows)
- Usage
- API reference
- Project layout
- Configuration
- Development notes
- Contributing
- License

Features
- Generate many timestamped log files concurrently with configurable lines-per-file and concurrency.
- Background generation with a thread pool; UI polls status in real time.
- List, view (bounded to 20k chars), download and delete files from a selected output directory (restricted to generated_logs).
- Case-insensitive filename search.
- Dark/light theme toggle and responsive layout.
- Safe path handling to prevent directory traversal.

Demo
- Open http://127.0.0.1:5000 after starting the app.
- UI includes controls for: number of files, lines per file, concurrency, directory selector, search, and file viewer.

Quickstart (Windows, recommended)
1. Clone repository
   ```
   git clone <repo-url>
   cd log_simulator
   ```
2. Create and activate virtual environment (PowerShell)
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies
   ```
   python -m pip install --upgrade pip
   python -m pip install Flask
   ```
   (Optional) create `requirements.txt` and run `python -m pip install -r requirements.txt`
4. Run
   ```
   python app.py
   ```
5. Open browser: http://127.0.0.1:5000

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
└─ requirements.txt            # recommended
```

Configuration
- Edit `GENERATED_DIR` in `app.py` to change the base output folder.
- `write_one_file()` controls file content and format; modify for custom log formats.
- File view limit: default 20,000 characters — change in `api_file_content` if needed.

Development notes
- Shared status is protected by a threading.Lock to avoid races.
- Long-running tasks run in background threads; the Flask dev server is for local use only. For production, use a WSGI server and add authentication.
- The app enforces safe path joining to prevent directory traversal.

Recommended .gitignore (basic)
```
.venv/
__pycache__/
generated_logs/
*.pyc
```

Contributing
- Keep changes small and documented.
- Add tests for path-safety and API behavior using temporary directories.
- Consider adding Server-Sent Events or WebSockets to replace polling for real-time UI.

License
- Add your preferred license file (e.g., MIT). If none provided, treat the project as unlicensed.

---

Tips for a polished GitHub repo
- Add a short GIF or screenshot to the README (place in `assets/`).
- Include a LICENSE file and a minimal CONTRIBUTING.md.
- Add CI checks for linting and unit tests (optional).
- Use `requirements.txt` for pinned dependencies.


