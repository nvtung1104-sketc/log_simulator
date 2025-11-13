# app.py
import os
import time
import threading
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, jsonify, send_from_directory, abort

app = Flask(__name__, static_folder='static', template_folder='templates')

# Config
GENERATED_DIR = "generated_logs"
MAX_FILE_PREVIEW_CHARS = 20000

# Ensure output dir exists
os.makedirs(GENERATED_DIR, exist_ok=True)

# Shared state protected by lock
status_lock = threading.Lock()
status = {
    "total_requested": 0,
    "created": 0,
    "in_progress": 0,
    "files": [],        # list of {"filename": str, "duration_ms": int}
    "started_at": None,
    "ended_at": None
}

# Current view directory (absolute path). Default to GENERATED_DIR
with status_lock:
    view_dir = os.path.abspath(GENERATED_DIR)


def safe_join_base(base: str, *parts: str) -> str:
    """Return absolute path for parts under base. Raise ValueError if outside base."""
    base_abs = os.path.abspath(base)
    candidate = os.path.abspath(os.path.join(base_abs, *parts))
    # Use commonpath to avoid prefix collisions
    if os.path.commonpath([base_abs, candidate]) != base_abs:
        raise ValueError("Path outside allowed base")
    return candidate


def write_one_file(file_index: int, lines_per_file: int, prefix: str = "clientlog"):
    """Create one log file and return (filename, duration_ms)."""
    start_ts = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}_{file_index:04d}.log"
    path = os.path.join(GENERATED_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            for i in range(1, max(1, int(lines_per_file)) + 1):
                ts = datetime.now().isoformat(sep=' ', timespec='milliseconds')
                line = f"{i} | {ts} | Simulated action #{i}\n"
                f.write(line)
        duration_ms = int((time.time() - start_ts) * 1000)
        return filename, duration_ms
    except Exception:
        # On failure, ensure no broken file remains
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        raise


def worker_create_files(num_files: int, lines_per_file: int, concurrency: int):
    """Background worker that creates files concurrently and updates status."""
    with status_lock:
        status["total_requested"] = int(num_files)
        status["created"] = 0
        status["in_progress"] = 0
        status["files"].clear()
        status["started_at"] = datetime.now().isoformat(sep=' ', timespec='seconds')
        status["ended_at"] = None

    with ThreadPoolExecutor(max_workers=max(1, int(concurrency))) as executor:
        futures = {}
        for idx in range(1, int(num_files) + 1):
            with status_lock:
                status["in_progress"] += 1
            fut = executor.submit(write_one_file, idx, lines_per_file)
            futures[fut] = idx

        for fut in as_completed(futures):
            try:
                filename, duration = fut.result()
            except Exception as e:
                filename = f"ERROR_{futures.get(fut, 'unknown')}"
                duration = 0
                app.logger.exception("Error creating file for task %s", futures.get(fut, 'unknown'))
            with status_lock:
                status["files"].append({"filename": filename, "duration_ms": duration})
                status["created"] += 1
                status["in_progress"] = max(0, status["in_progress"] - 1)

    with status_lock:
        status["ended_at"] = datetime.now().isoformat(sep=' ', timespec='seconds')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True) or {}
    try:
        num_files = int(data.get("num_files", 1))
        lines_per_file = int(data.get("lines_per_file", 3000))
        concurrency = int(data.get("concurrency", min(4, os.cpu_count() or 4)))
    except Exception:
        return jsonify({"error": "invalid parameters"}), 400

    thread = threading.Thread(
        target=worker_create_files,
        args=(num_files, lines_per_file, concurrency),
        daemon=True
    )
    thread.start()
    return jsonify({"status": "started", "num_files": num_files, "lines_per_file": lines_per_file, "concurrency": concurrency})


@app.route("/api/status", methods=["GET"])
def api_status():
    with status_lock:
        copy_files = list(status["files"])
        created = status["created"]
        total = status["total_requested"]
        in_progress = status["in_progress"]
        started_at = status["started_at"]
        ended_at = status["ended_at"]

    durations = [f.get("duration_ms", 0) for f in copy_files if isinstance(f.get("duration_ms", None), (int, float))]
    total_ms = sum(durations)
    count = len(durations)
    agg = {
        "files_count": count,
        "total_ms": total_ms,
        "avg_ms": int(total_ms / count) if count else 0,
        "min_ms": min(durations) if durations else 0,
        "max_ms": max(durations) if durations else 0
    }
    # Return recent files (most recent last)
    recent = list(copy_files)[-50:]
    return jsonify({
        "total_requested": total,
        "created": created,
        "in_progress": in_progress,
        "files": recent,
        "started_at": started_at,
        "ended_at": ended_at,
        "aggregates": agg
    })


@app.route("/api/list_dirs", methods=["GET"])
def api_list_dirs():
    base = os.path.abspath(GENERATED_DIR)
    dirs = []
    # include base itself as relative path from cwd
    try:
        dirs.append(os.path.relpath(base, start=os.getcwd()))
        for entry in sorted(os.listdir(base)):
            p = os.path.join(base, entry)
            if os.path.isdir(p):
                dirs.append(os.path.relpath(p, start=os.getcwd()))
    except Exception:
        pass
    return jsonify({"dirs": dirs})


@app.route("/api/set_view_dir", methods=["POST"])
def api_set_view_dir():
    data = request.get_json(silent=True) or {}
    d = data.get("dir", GENERATED_DIR)
    base = os.path.abspath(GENERATED_DIR)
    try:
        candidate = os.path.abspath(d) if os.path.isabs(d) else os.path.abspath(os.path.join(os.getcwd(), d))
        if os.path.commonpath([base, candidate]) != base:
            return jsonify({"error": "dir must be under generated_logs"}), 400
        if not os.path.isdir(candidate):
            return jsonify({"error": "not a directory"}), 400
        with status_lock:
            global view_dir
            view_dir = candidate
        return jsonify({"dir": os.path.relpath(view_dir, start=os.getcwd())})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/list_files", methods=["GET"])
def api_list_files():
    with status_lock:
        vd = view_dir
    try:
        files = sorted([f for f in os.listdir(vd) if os.path.isfile(os.path.join(vd, f))])
    except Exception:
        files = []
    return jsonify({"files": files, "dir": os.path.relpath(vd, start=os.getcwd())})


@app.route("/api/search", methods=["GET"])
def api_search():
    q = (request.args.get("q") or "").strip()
    with status_lock:
        vd = view_dir
    if not q:
        return jsonify({"files": []})
    try:
        allf = [f for f in os.listdir(vd) if os.path.isfile(os.path.join(vd, f))]
    except Exception:
        allf = []
    matches = [fn for fn in allf if q.lower() in fn.lower()]
    return jsonify({"files": matches})


@app.route("/api/file_content", methods=["GET"])
def api_file_content():
    filename = request.args.get("filename", "")
    with status_lock:
        vd = view_dir
    if not filename:
        return jsonify({"error": "missing filename"}), 400
    try:
        safe_path = safe_join_base(vd, filename)
        if not os.path.isfile(safe_path):
            return jsonify({"error": "not found"}), 404
        # Read up to MAX_FILE_PREVIEW_CHARS characters
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_FILE_PREVIEW_CHARS)
        return jsonify({"filename": filename, "content": content})
    except ValueError:
        return jsonify({"error": "invalid path"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete_file", methods=["POST"])
def api_delete_file():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    with status_lock:
        vd = view_dir
    if not filename:
        return jsonify({"error": "missing filename"}), 400
    try:
        safe_path = safe_join_base(vd, filename)
        if not os.path.isfile(safe_path):
            return jsonify({"error": "not found"}), 404
        os.remove(safe_path)
        return jsonify({"deleted": filename})
    except ValueError:
        return jsonify({"error": "invalid path"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    with status_lock:
        vd = view_dir
    try:
        # send_from_directory will check path; ensure safety first
        safe_path = safe_join_base(vd, filename)
        if not os.path.isfile(safe_path):
            abort(404)
        return send_from_directory(vd, filename, as_attachment=True)
    except ValueError:
        abort(400)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Log Generator Simulator")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug")
    args = parser.parse_args()

    # Run Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)
