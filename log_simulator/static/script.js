// static/script.js
async function startGenerate() {
  const numFiles = parseInt(document.getElementById('numFiles').value || '1', 10);
  const linesPerFile = parseInt(document.getElementById('linesPerFile').value || '3000', 10);
  const concurrency = parseInt(document.getElementById('concurrency').value || '4', 10);

  const resp = await fetch('/api/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({num_files: numFiles, lines_per_file: linesPerFile, concurrency})
  });
  const j = await resp.json();
  console.log('started', j);
  pollStatus();
}

let pollInterval = null;
async function pollStatus() {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    try {
      const r = await fetch('/api/status');
      const j = await r.json();
      updateStatusUI(j);
      if (j.ended_at && j.created === j.total_requested) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
    } catch (e) {
      console.error('poll error', e);
    }
  }, 1000);
}

function updateStatusUI(data) {
  document.getElementById('startedAt').innerText = data.started_at || '-';
  document.getElementById('endedAt').innerText = data.ended_at || '-';
  document.getElementById('requested').innerText = data.total_requested;
  document.getElementById('created').innerText = data.created;
  document.getElementById('inprogress').innerText = data.in_progress;

  const agg = data.aggregates || {};
  document.getElementById('aggFiles').innerText = agg.files_count || 0;
  document.getElementById('aggTotal').innerText = agg.total_ms || 0;
  document.getElementById('aggAvg').innerText = agg.avg_ms || 0;
  document.getElementById('aggMin').innerText = agg.min_ms || 0;
  document.getElementById('aggMax').innerText = agg.max_ms || 0;

  const recent = data.files || [];
  const recentList = document.getElementById('recentList');
  recentList.innerHTML = '';
  recent.forEach(f => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#';
    a.textContent = `${f.filename} (${f.duration_ms} ms)`;
    a.addEventListener('click', (e) => { e.preventDefault(); fetchAndShowFile(f.filename); });
    li.appendChild(a);
    recentList.appendChild(li);
  });
}

async function listFiles(dirOverride) {
  const q = dirOverride ? `/api/list_files?dir=${encodeURIComponent(dirOverride)}` : '/api/list_files';
  const r = await fetch(q);
  const j = await r.json();
  const list = document.getElementById('allFiles');
  const dirLabel = document.getElementById('dirLabel');
  const currentDir = document.getElementById('currentDir');
  list.innerHTML = '';
  dirLabel.innerText = j.dir || '';
  currentDir.innerText = j.dir || '';
  (j.files || []).forEach(fn => {
    const li = document.createElement('li');

    const left = document.createElement('div');
    left.style.flex = "1";
    left.style.overflow = "hidden";
    const a = document.createElement('a');
    a.href = `/download/${encodeURIComponent(fn)}`;
    a.textContent = fn;
    a.target = '_blank';
    a.style.color = 'inherit';
    a.style.textDecoration = 'none';
    left.appendChild(a);

    const actions = document.createElement('div');
    actions.style.display = 'flex';
    actions.style.gap = '8px';

    const viewBtn = document.createElement('button');
    viewBtn.textContent = 'Xem';
    viewBtn.title = 'Xem nội dung';
    viewBtn.addEventListener('click', () => fetchAndShowFile(fn));
    actions.appendChild(viewBtn);

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Xóa';
    delBtn.title = 'Xóa file';
    delBtn.className = 'danger';
    delBtn.addEventListener('click', async () => {
      if (!confirm(`Bạn có chắc muốn xóa file "${fn}" ?`)) return;
      try {
        const res = await fetch('/api/delete_file', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({filename: fn})
        });
        const j = await res.json();
        if (j.deleted) {
          // refresh lists
          await listFiles();
          // Nếu hàm searchFiles tồn tại, gọi cập nhật kết quả tìm kiếm
          if (typeof searchFiles === 'function') {
            try { await searchFiles(); } catch (e) { /* ignore */ }
          }
          // clear viewer if showing same file
          const box = document.getElementById('fileContent');
          if (box && box.dataset && box.dataset.filename === fn) {
            box.textContent = 'File đã bị xóa.';
            box.dataset.filename = '';
          }
        } else {
          alert('Lỗi: ' + (j.error || 'Không thể xóa'));
        }
      } catch (e) {
        alert('Lỗi khi xóa: ' + e);
      }
    });
    actions.appendChild(delBtn);

    li.appendChild(left);
    li.appendChild(actions);
    list.appendChild(li);
  });
}

async function fetchDirs() {
  const r = await fetch('/api/list_dirs');
  const j = await r.json();
  const sel = document.getElementById('dirSelect');
  sel.innerHTML = '';
  (j.dirs || []).forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = d;
    sel.appendChild(opt);
  });
}

async function setViewDir() {
  const sel = document.getElementById('dirSelect');
  const dir = sel.value;
  const r = await fetch('/api/set_view_dir', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({dir})
  });
  const j = await r.json();
  if (j.error) {
    alert('Error: ' + j.error);
  } else {
    await listFiles();
  }
}

// Đảm bảo hàm searchFiles được định nghĩa (đã fix ReferenceError)
async function searchFiles() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) {
    // clear results if empty
    const list = document.getElementById('searchResults');
    if (list) list.innerHTML = '';
    return;
  }
  const r = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  const j = await r.json();
  const list = document.getElementById('searchResults');
  list.innerHTML = '';
  (j.files || []).forEach(fn => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#';
    a.textContent = fn;
    a.addEventListener('click', (e) => { e.preventDefault(); fetchAndShowFile(fn); });
    li.appendChild(a);
    list.appendChild(li);
  });
}

async function fetchAndShowFile(filename) {
  const r = await fetch(`/api/file_content?filename=${encodeURIComponent(filename)}`);
  const j = await r.json();
  const box = document.getElementById('fileContent');
  if (j.error) {
    box.textContent = `Error: ${j.error}`;
    if (box) box.dataset.filename = '';
  } else {
    box.textContent = j.content || '';
    if (box) box.dataset.filename = filename;
  }
}

// theme toggle
const themeToggleEl = document.getElementById('themeToggle');
if (themeToggleEl) {
  themeToggleEl.addEventListener('change', (e) => {
    if (e.target.checked) document.body.classList.add('dark');
    else document.body.classList.remove('dark');
  });
}

// Event bindings (guard if elements missing)
const startBtn = document.getElementById('startBtn');
if (startBtn) startBtn.addEventListener('click', startGenerate);
const refreshBtn = document.getElementById('refreshBtn');
if (refreshBtn) refreshBtn.addEventListener('click', () => { if (!pollInterval) pollStatus(); });
const listBtn = document.getElementById('listFilesBtn');
if (listBtn) listBtn.addEventListener('click', listFiles);
const setDirBtn = document.getElementById('setDirBtn');
if (setDirBtn) setDirBtn.addEventListener('click', setViewDir);
const searchBtn = document.getElementById('searchBtn');
if (searchBtn) searchBtn.addEventListener('click', searchFiles);
const searchInput = document.getElementById('searchInput');
if (searchInput) searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') searchFiles(); });

// initial poll to populate UI
pollStatus();
fetchDirs().then(listFiles);
