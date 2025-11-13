# Log Generator Simulator — Project README

## Overview
Log Generator Simulator is a lightweight local tool that creates synthetic log files for testing, demos, and load experiments. It provides a web UI to generate multiple files concurrently, monitor progress, list and search files, view contents (bounded), download, and delete files. All file operations are restricted to a configurable output folder to reduce risk.

## Key features
- Generate many log files with configurable lines per file and concurrency.
- Background generation with thread pool; UI polls status.
- Directory selector restricted to the generated output and its subfolders.
- File listing, case-insensitive filename search, view (up to 20k chars), download and delete.
- Dark-themed responsive single-page UI (vanilla JS + CSS).
- Simple, local-only Flask backend.

## Core algorithm
- write_one_file(file_index, lines_per_file):
  - Creates a timestamped filename and writes sequential lines with timestamps and simple simulated text.
  - Measures and returns the write duration in milliseconds.
- worker_create_files(num_files, lines_per_file, concurrency):
  - Runs a ThreadPoolExecutor with max_workers equal to the configured concurrency.
  - Submits write tasks and uses as_completed to update shared status when each file finishes.
- Concurrency & safety:
  - Shared status is protected by a threading.Lock to prevent race conditions.
  - UI polls /api/status periodically (default 1s) for updates.
- Limits:
  - File content reads are capped (e.g., 20k characters) to avoid heavy responses.

## Directory structure
Recommended layout:

.
├─ .venv/                       # optional Python virtual environment (not committed)  
├─ generated_logs/              # runtime output (created automatically)  
│  └─ (log files and subfolders)  
├─ static/                      
│  ├─ script.js                  # frontend JS (fetch and UI logic)  
│  └─ style.css                  # CSS theme and layout  
├─ templates/                    
│  └─ index.html                 # single-page UI  
├─ app.py                        # Flask backend, APIs, worker  
├─ README.md                     # this document  
└─ requirements.txt              # optional pinned deps (Flask)

Notes:
- Only generated_logs and its subdirectories are allowed for view/download/delete via the UI.

## User interface (UI)
- Theme: dark by default, with a toggle to switch.
- Controls:
  - Number of files, lines per file, concurrency.
  - Start generation, refresh status.
  - Directory dropdown (shows generated_logs and subfolders) and "Apply" button.
  - Search box for filename substring (case-insensitive).
- Panels:
  - Status panel: started/ended timestamps, requested/created/in-progress counters.
  - Aggregates: count, total/avg/min/max durations (ms).
  - Files panel: files in selected directory with View, Download, Delete actions.
  - Recent & Search results lists.
  - Viewer: shows up to configured character limit (default 20k) in a scrollable, monospace block.

## API endpoints (summary)
- GET / — serve UI (index.html)
- POST /api/generate — start generation; body: { num_files, lines_per_file, concurrency }
- GET /api/status — return status and recent file entries
- GET /api/list_dirs — list allowed view directories (generated_logs + subdirs)
- POST /api/set_view_dir — set current view directory; body: { dir }
- GET /api/list_files — list files in current view_dir
- GET /api/search?q=... — filename substring search in view_dir
- GET /api/file_content?filename=... — return bounded file content (safe-joined)
- POST /api/delete_file — delete file in view_dir; body: { filename }
- GET /download/<filename> — download file from current view_dir

## Installation (Windows, recommended)
1. Create and activate a virtual environment (PowerShell):
   - python -m venv .venv
   - .\.venv\Scripts\Activate.ps1
2. Install dependencies:
   - python -m pip install --upgrade pip
   - python -m pip install Flask
   - (optional) python -m pip install -r requirements.txt
3. Run the application:
   - python app.py
4. Open http://127.0.0.1:5000 in your browser.

## Basic usage
1. Set Number of files, Lines per file, Concurrency.
2. Click "Start Generate".
3. Monitor progress via the Status panel; recent files appear automatically.
4. Choose a directory from the dropdown and click "Apply" to list files.
5. Use View to display file content, Download to save, or Delete to remove (confirmation required).
6. Use Search to find files by substring (case-insensitive).

## Configuration & advanced options
- GENERATED_DIR in app.py controls base output directory and the allowed scope for file operations.
- Adjust the content format and rate by editing write_one_file().
- Tune concurrency to match host capabilities. For CPU-bound or very heavy I/O, consider process-based workers or queued tasks.
- Replace polling with Server-Sent Events (SSE) or WebSocket for real-time updates.

## Security & limitations
- This tool is intended for local, trusted use. It lacks authentication and production hardening.
- All UI file operations are constrained to GENERATED_DIR and its children via safe path joining to mitigate directory traversal.
- File viewer is truncated to a safe limit to protect the server and browser.
- Deletions are permanent—use with caution.
- If exposing to a network, add authentication, run behind a production WSGI server, and enable HTTPS.

## Development notes
- Keep status updates and file operations under a lock to avoid race conditions.
- Use safe_join_base (or equivalent) to ensure path security.
- Maintain consistent DOM element IDs if you alter templates; script.js expects specific IDs.
- Add tests that use temporary directories to validate safe path logic and API behavior.
- Use requirements.txt to lock dependency versions for reproducible environments.

## Testing suggestions
- Manual: generate small and large batches, verify counts and aggregates, test view/search/delete flows.
- Automated: write pytest tests for:
  - safe path joining and directory restrictions
  - API semantics (generate, status, list, search, file_content, delete)
  - concurrent generation correctness (use temporary dirs)

## License & contact
- No license included by default. Add a LICENSE file (MIT, Apache-2.0, etc.) if you plan to share.
- For local development questions, open issues or contact the project maintainer (add contact details here).


