"""Trang demo — giao diện chat gọi vào chính API của service này.

Không thuộc yêu cầu chấm điểm của lab; thêm vào để demo trực quan thay vì
phải gõ curl. Trang này phục vụ ở `GET /`, gọi `POST /ask` cùng origin nên
không dính CORS, và không đọc secret nào từ server — API key do người dùng
tự nhập ở trình duyệt.
"""

from __future__ import annotations

DEMO_PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Day 12 Production Agent — Demo</title>
<style>
  :root {
    --bg: #f7f7f8;      --panel: #ffffff;   --ink: #1c1c1e;
    --muted: #6b6b70;   --line: #e3e3e6;    --accent: #2563eb;
    --user-bg: #2563eb; --user-ink: #ffffff;
    --ok: #16a34a;      --warn: #d97706;    --err: #dc2626;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #17171a;    --panel: #202024;   --ink: #ececf1;
      --muted: #9a9aa3; --line: #33333a;    --accent: #4f8cff;
      --user-bg: #2f6fe4; --user-ink: #ffffff;
      --ok: #4ade80;    --warn: #fbbf24;    --err: #f87171;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    display: flex; justify-content: center; padding: 24px 16px;
  }
  .wrap { width: 100%; max-width: 760px; }
  header { margin-bottom: 16px; }
  h1 { font-size: 20px; margin: 0 0 6px; letter-spacing: -0.01em; }
  .sub { color: var(--muted); font-size: 13px; }
  .pills { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
  .pill {
    font-size: 12px; padding: 3px 10px; border-radius: 999px;
    border: 1px solid var(--line); background: var(--panel); color: var(--muted);
    display: inline-flex; align-items: center; gap: 6px;
  }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--muted); }
  .dot.up { background: var(--ok); }
  .dot.down { background: var(--err); }
  .panel {
    background: var(--panel); border: 1px solid var(--line);
    border-radius: 12px; padding: 14px;
  }
  .settings { display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 14px; }
  @media (max-width: 560px) { .settings { grid-template-columns: 1fr; } }
  label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
  input, textarea {
    width: 100%; padding: 9px 11px; border-radius: 8px; font: inherit;
    border: 1px solid var(--line); background: var(--bg); color: var(--ink);
  }
  input:focus, textarea:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
  #log { min-height: 220px; max-height: 46vh; overflow-y: auto; margin-bottom: 12px; }
  .empty { color: var(--muted); font-size: 14px; text-align: center; padding: 60px 20px; }
  .msg { display: flex; margin-bottom: 10px; }
  .msg.me { justify-content: flex-end; }
  .bubble {
    max-width: 78%; padding: 9px 13px; border-radius: 14px;
    border: 1px solid var(--line); background: var(--bg); white-space: pre-wrap;
  }
  .msg.me .bubble { background: var(--user-bg); color: var(--user-ink); border-color: transparent; }
  .meta { font-size: 11px; color: var(--muted); margin-top: 5px; }
  .msg.err .bubble { border-color: var(--err); color: var(--err); }
  .composer { display: flex; gap: 8px; align-items: flex-end; }
  textarea { resize: vertical; min-height: 44px; max-height: 160px; }
  button {
    padding: 10px 18px; border-radius: 8px; border: 0; cursor: pointer;
    background: var(--accent); color: #fff; font: inherit; font-weight: 500;
  }
  button:disabled { opacity: .5; cursor: default; }
  .stats {
    display: flex; gap: 18px; flex-wrap: wrap;
    margin-top: 12px; font-size: 12px; color: var(--muted);
  }
  .stats b { color: var(--ink); font-variant-numeric: tabular-nums; font-weight: 600; }
  code { font-family: ui-monospace, "Cascadia Code", Consolas, monospace; font-size: 12px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Day 12 Production Agent</h1>
    <div class="sub">Giao diện demo gọi vào <code>POST /ask</code> của chính service này.</div>
    <div class="pills">
      <span class="pill"><span class="dot" id="d-health"></span>/health</span>
      <span class="pill"><span class="dot" id="d-ready"></span>/ready</span>
      <span class="pill" id="p-version">version —</span>
    </div>
  </header>

  <div class="panel">
    <div class="settings">
      <div>
        <label for="key">X-API-Key</label>
        <input id="key" type="password" placeholder="khóa AGENT_API_KEY" autocomplete="off">
      </div>
      <div>
        <label for="uid">X-User-Id</label>
        <input id="uid" type="text" value="demo" autocomplete="off">
      </div>
    </div>

    <div id="log">
      <div class="empty">Nhập API key rồi đặt câu hỏi.<br>Hỏi nhiều lần cùng một User Id để thấy agent nhớ lịch sử.</div>
    </div>

    <div class="composer">
      <textarea id="q" rows="1" placeholder="Hỏi gì đó… (Enter để gửi)"></textarea>
      <button id="send">Gửi</button>
    </div>

    <div class="stats">
      <span>Lượt hỏi <b id="s-turns">0</b></span>
      <span>history_length <b id="s-hist">0</b></span>
      <span>Tổng chi phí <b id="s-cost">$0.000000</b></span>
      <span>Tokens <b id="s-tok">0</b></span>
    </div>
  </div>
</div>

<script>
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var log = $('log'), keyEl = $('key'), uidEl = $('uid'), qEl = $('q'), btn = $('send');
  var turns = 0, cost = 0, tokens = 0;

  // Khóa chỉ nằm ở trình duyệt, không gửi đi đâu ngoài service này
  try {
    var saved = localStorage.getItem('day12_key');
    if (saved) keyEl.value = saved;
  } catch (e) {}
  keyEl.addEventListener('change', function () {
    try { localStorage.setItem('day12_key', keyEl.value); } catch (e) {}
  });

  function probe(path, dot) {
    fetch(path).then(function (r) {
      dot.className = 'dot ' + (r.ok ? 'up' : 'down');
      return r.ok ? r.json() : null;
    }).then(function (d) {
      if (d && d.version) $('p-version').textContent = 'version ' + d.version;
    }).catch(function () { dot.className = 'dot down'; });
  }
  probe('/health', $('d-health'));
  probe('/ready', $('d-ready'));
  setInterval(function () {
    probe('/health', $('d-health'));
    probe('/ready', $('d-ready'));
  }, 15000);

  function bubble(text, cls, meta) {
    var empty = log.querySelector('.empty');
    if (empty) empty.remove();
    var row = document.createElement('div');
    row.className = 'msg ' + cls;
    var b = document.createElement('div');
    b.className = 'bubble';
    b.textContent = text;
    if (meta) {
      var m = document.createElement('div');
      m.className = 'meta';
      m.textContent = meta;
      b.appendChild(m);
    }
    row.appendChild(b);
    log.appendChild(row);
    log.scrollTop = log.scrollHeight;
  }

  // Mỗi mã lỗi của API tương ứng một lớp bảo vệ đã cài ở CP3
  var EXPLAIN = {
    401: 'API key sai hoặc thiếu — cổng xác thực chặn.',
    402: 'Vượt ngân sách tháng (MONTHLY_BUDGET_USD) — cost guard chặn.',
    429: 'Quá 10 request/phút — rate limiter chặn, thử lại sau 60 giây.',
    503: 'Service chưa sẵn sàng (thường là mất kết nối Redis).'
  };

  function send() {
    var q = qEl.value.trim();
    if (!q) return;
    if (!keyEl.value) { bubble('Chưa nhập X-API-Key.', 'err'); return; }

    bubble(q, 'me');
    qEl.value = '';
    btn.disabled = true;

    fetch('/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': keyEl.value,
        'X-User-Id': uidEl.value || 'demo'
      },
      body: JSON.stringify({ question: q })
    }).then(function (r) {
      return r.json().then(function (d) { return { status: r.status, body: d }; });
    }).then(function (res) {
      if (res.status !== 200) {
        var why = EXPLAIN[res.status] || (typeof res.body.detail === 'string' ? res.body.detail : '');
        bubble('HTTP ' + res.status + ' — ' + why, 'err');
        return;
      }
      var d = res.body;
      turns += 1;
      cost += d.cost_usd;
      tokens += d.tokens['in'] + d.tokens.out;
      bubble(d.answer, 'bot',
        'history_length=' + d.history_length +
        ' · ' + d.tokens['in'] + '→' + d.tokens.out + ' tokens' +
        ' · $' + d.cost_usd.toFixed(6));
      $('s-turns').textContent = turns;
      $('s-hist').textContent = d.history_length;
      $('s-cost').textContent = '$' + cost.toFixed(6);
      $('s-tok').textContent = tokens;
    }).catch(function (e) {
      bubble('Không gọi được service: ' + e.message, 'err');
    }).then(function () {
      btn.disabled = false;
      qEl.focus();
    });
  }

  btn.addEventListener('click', send);
  qEl.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
})();
</script>
</body>
</html>
"""
