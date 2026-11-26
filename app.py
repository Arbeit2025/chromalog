# chromalog - 今日の色ログ
# 1日を1色で記録する日記。月カレンダーの各日に色とひとことメモを残す。
# 記録はブラウザの localStorage にのみ保存され、サーバーには送信されない。
import json

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# プリセットカラー（hex は #rrggbb 形式、name は表示用の色名）
PRESET_COLORS = [
    {"hex": "#f6c9d4", "name": "さくら"},
    {"hex": "#f194a6", "name": "もも"},
    {"hex": "#e5484d", "name": "あか"},
    {"hex": "#ff9d76", "name": "サンゴ"},
    {"hex": "#e8833a", "name": "だいだい"},
    {"hex": "#ffd9a0", "name": "あんず"},
    {"hex": "#f2b544", "name": "やまぶき"},
    {"hex": "#f2e394", "name": "ひまわり"},
    {"hex": "#f7e463", "name": "レモン"},
    {"hex": "#b7d977", "name": "わかくさ"},
    {"hex": "#5da85f", "name": "みどり"},
    {"hex": "#588157", "name": "もり"},
    {"hex": "#2e7d5b", "name": "ふかみどり"},
    {"hex": "#7fc8bc", "name": "ミント"},
    {"hex": "#56b8c7", "name": "みずいろ"},
    {"hex": "#8fd0f2", "name": "そら"},
    {"hex": "#3a7bd5", "name": "あお"},
    {"hex": "#345995", "name": "あいいろ"},
    {"hex": "#2b3a67", "name": "こん"},
    {"hex": "#7d6bb5", "name": "ふじ"},
    {"hex": "#b388c7", "name": "ラベンダー"},
    {"hex": "#e3b7e0", "name": "ゆめ"},
    {"hex": "#a9746e", "name": "ちゃ"},
    {"hex": "#7a4a2b", "name": "こげちゃ"},
    {"hex": "#d9c6a5", "name": "ベージュ"},
    {"hex": "#f5efe0", "name": "きなり"},
    {"hex": "#ffffff", "name": "しろ"},
    {"hex": "#c0c4cc", "name": "ぎん"},
    {"hex": "#6b7280", "name": "はいいろ"},
    {"hex": "#26221f", "name": "すみ"},
]

CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: #fcfcfa; color: #33302b;
  font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic", "YuGothic", sans-serif;
  line-height: 1.7;
}
header { text-align: center; padding: 2.6rem 1rem 0.6rem; }
header h1 {
  font-family: "Hiragino Mincho ProN", "Yu Mincho", "YuMincho", Georgia, serif;
  font-size: 1.7rem; letter-spacing: 0.3em; margin: 0; font-weight: 600;
}
header p { color: #8d867a; font-size: 0.88rem; letter-spacing: 0.14em; margin: 0.4rem 0 0; }
main { max-width: 720px; margin: 0 auto; padding: 1.4rem 1rem 3rem; }
.cal-head {
  display: flex; align-items: center; justify-content: space-between;
  margin: 1.2rem 0 0.8rem;
}
.cal-head h2 {
  font-family: "Hiragino Mincho ProN", "Yu Mincho", "YuMincho", Georgia, serif;
  font-size: 1.2rem; letter-spacing: 0.18em; margin: 0; font-weight: 600;
}
button {
  font-family: inherit; background: transparent; color: #4a453c;
  border: 1px solid #cfc9bc; border-radius: 999px; cursor: pointer;
  padding: 0.35rem 1rem; font-size: 0.85rem; letter-spacing: 0.08em;
}
button:hover { background: #f1eee6; }
.weekdays {
  display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px;
  text-align: center; font-size: 0.78rem; color: #8d867a; letter-spacing: 0.2em;
  margin-bottom: 6px;
}
.weekdays .sun { color: #c0564f; }
.weekdays .sat { color: #4f6fc0; }
.calendar { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px; }
.day {
  border: 1px solid #e7e3d9; border-radius: 8px; background: #fff;
  min-height: 74px; padding: 5px 6px; text-align: left; cursor: pointer;
  display: flex; flex-direction: column; gap: 3px; font-family: inherit;
}
.day:hover { border-color: #b9b2a2; }
.day.empty-cell { border: none; background: transparent; cursor: default; }
.day .dnum { font-size: 0.8rem; color: #6d675c; line-height: 1.2; }
.day.today .dnum { font-weight: 700; color: #26221f; text-decoration: underline; }
.day.selected { outline: 2px solid #4a453c; outline-offset: 1px; }
.day .swatch { flex: 1; border-radius: 4px; border: 1px solid #e7e3d9; min-height: 18px; }
.day .memo {
  font-size: 0.62rem; color: #6d675c; line-height: 1.3;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.summary { text-align: center; color: #6d675c; font-size: 0.9rem; margin: 1.4rem 0 0; }
.summary .sum-swatch {
  display: inline-block; width: 0.95em; height: 0.95em; border-radius: 3px;
  border: 1px solid #cfc9bc; vertical-align: -0.12em; margin: 0 0.25em;
}
.editor {
  margin-top: 2rem; border: 1px solid #e0dbcf; border-radius: 12px;
  background: #fff; padding: 1.4rem 1.5rem 1.5rem;
}
.editor h3 {
  font-family: "Hiragino Mincho ProN", "Yu Mincho", "YuMincho", Georgia, serif;
  font-size: 1.05rem; letter-spacing: 0.12em; margin: 0 0 1rem; font-weight: 600;
}
.editor-row { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1rem; }
input[type=color] {
  width: 64px; height: 40px; border: 1px solid #cfc9bc; border-radius: 8px;
  background: #fff; padding: 3px; cursor: pointer;
}
#color-value { font-size: 0.9rem; color: #6d675c; letter-spacing: 0.06em; }
.swatches {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(34px, 1fr));
  gap: 7px; margin-bottom: 1.1rem;
}
.swatches button {
  height: 34px; border-radius: 7px; border: 1px solid #ddd8cc; padding: 0;
}
.swatches button.chosen { outline: 2px solid #4a453c; outline-offset: 1px; }
.memo-label { display: block; font-size: 0.85rem; color: #6d675c; letter-spacing: 0.08em; }
input[type=text] {
  width: 100%; font-family: inherit; font-size: 1rem; padding: 0.5rem 0.7rem;
  border: 1px solid #cfc9bc; border-radius: 8px; margin-top: 0.35rem; color: inherit;
  background: #fff;
}
.editor-actions { margin-top: 1.2rem; display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.editor-actions #save-btn { background: #3d382f; color: #f7f4ec; border-color: #3d382f; }
.editor-actions #save-btn:hover { background: #574f41; }
#editor-msg { font-size: 0.85rem; color: #5da85f; }
.hint { text-align: center; color: #a39b8b; font-size: 0.8rem; margin-top: 2.2rem; }
footer { text-align: center; color: #a39b8b; font-size: 0.8rem; padding: 0 1rem 2rem; }
@media (max-width: 560px) {
  .day { min-height: 58px; padding: 4px; }
  .day .memo { display: none; }
  header h1 { font-size: 1.4rem; }
}
"""

SCRIPT = """
var PRESETS = __PRESETS_JSON__;
var STORAGE_KEY = 'chromalog-v1';
var WEEKDAYS = ['日', '月', '火', '水', '木', '金', '土'];

var entries = loadEntries();
var now = new Date();
var viewYear = now.getFullYear();
var viewMonth = now.getMonth();
var selectedKey = null;
var selectedColor = PRESETS[2].hex;

function loadEntries() {
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) { return {}; }
    var data = JSON.parse(raw);
    if (data && typeof data === 'object' && !Array.isArray(data)) { return data; }
    return {};
  } catch (e) {
    return {};
  }
}

function storeEntries() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  } catch (e) {}
}

function pad(n) { return (n < 10 ? '0' : '') + n; }

function dateKey(y, m, d) { return y + '-' + pad(m + 1) + '-' + pad(d); }

function presetName(hex) {
  for (var i = 0; i < PRESETS.length; i++) {
    if (PRESETS[i].hex.toLowerCase() === String(hex).toLowerCase()) {
      return PRESETS[i].name;
    }
  }
  return hex;
}

function renderCalendar() {
  var label = document.getElementById('month-label');
  label.textContent = viewYear + '年 ' + (viewMonth + 1) + '月';

  var cal = document.getElementById('calendar');
  cal.innerHTML = '';

  var first = new Date(viewYear, viewMonth, 1);
  var startDay = first.getDay();
  var daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  var todayKey = dateKey(now.getFullYear(), now.getMonth(), now.getDate());

  var i, cell;
  for (i = 0; i < startDay; i++) {
    cell = document.createElement('div');
    cell.className = 'day empty-cell';
    cal.appendChild(cell);
  }
  for (var d = 1; d <= daysInMonth; d++) {
    (function (dayNum) {
      var key = dateKey(viewYear, viewMonth, dayNum);
      var entry = entries[key];
      cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'day' + (key === todayKey ? ' today' : '') + (key === selectedKey ? ' selected' : '');

      var num = document.createElement('span');
      num.className = 'dnum';
      num.textContent = dayNum;
      cell.appendChild(num);

      var sw = document.createElement('span');
      sw.className = 'swatch';
      if (entry && entry.color) { sw.style.background = entry.color; }
      cell.appendChild(sw);

      var memo = document.createElement('span');
      memo.className = 'memo';
      memo.textContent = entry && entry.memo ? entry.memo : '';
      cell.appendChild(memo);

      cell.addEventListener('click', function () { openEditor(key); });
      cal.appendChild(cell);
    })(d);
  }
  renderSummary();
}

function renderSummary() {
  var prefix = viewYear + '-' + pad(viewMonth + 1) + '-';
  var count = 0;
  var colorCounts = {};
  for (var key in entries) {
    if (key.indexOf(prefix) === 0 && entries[key] && entries[key].color) {
      count++;
      var c = entries[key].color;
      colorCounts[c] = (colorCounts[c] || 0) + 1;
    }
  }
  var el = document.getElementById('summary');
  el.innerHTML = '';
  if (count === 0) {
    el.textContent = '今月の記録はまだありません。日付をクリックして、今日の色を残しましょう。';
    return;
  }
  var best = null;
  var bestCount = 0;
  for (var hex in colorCounts) {
    if (colorCounts[hex] > bestCount) { best = hex; bestCount = colorCounts[hex]; }
  }
  var text = document.createElement('span');
  text.textContent = '今月の記録： ' + count + '日 ／ よく使った色： ';
  el.appendChild(text);
  var sw = document.createElement('span');
  sw.className = 'sum-swatch';
  sw.style.background = best;
  el.appendChild(sw);
  var name = document.createElement('span');
  name.textContent = presetName(best) + '（' + bestCount + '日）';
  el.appendChild(name);
}

function buildSwatches() {
  var wrap = document.getElementById('swatches');
  wrap.innerHTML = '';
  PRESETS.forEach(function (p) {
    var b = document.createElement('button');
    b.type = 'button';
    b.style.background = p.hex;
    b.title = p.name + ' ' + p.hex;
    b.setAttribute('data-hex', p.hex);
    b.addEventListener('click', function () { setColor(p.hex); });
    wrap.appendChild(b);
  });
}

function setColor(hex) {
  selectedColor = hex;
  document.getElementById('color-input').value = hex;
  document.getElementById('color-value').textContent = presetName(hex) + ' ' + hex;
  var buttons = document.getElementById('swatches').children;
  for (var i = 0; i < buttons.length; i++) {
    var h = buttons[i].getAttribute('data-hex');
    if (h && h.toLowerCase() === String(hex).toLowerCase()) {
      buttons[i].classList.add('chosen');
    } else {
      buttons[i].classList.remove('chosen');
    }
  }
}

function openEditor(key) {
  selectedKey = key;
  var parts = key.split('-');
  var y = parseInt(parts[0], 10);
  var m = parseInt(parts[1], 10) - 1;
  var d = parseInt(parts[2], 10);
  var wd = WEEKDAYS[new Date(y, m, d).getDay()];
  document.getElementById('editor-date').textContent =
    y + '年' + (m + 1) + '月' + d + '日（' + wd + '）';
  var entry = entries[key];
  setColor(entry && entry.color ? entry.color : PRESETS[2].hex);
  document.getElementById('memo-input').value = entry && entry.memo ? entry.memo : '';
  document.getElementById('delete-btn').style.display = entry ? '' : 'none';
  document.getElementById('editor-msg').textContent = '';
  var editor = document.getElementById('editor');
  editor.hidden = false;
  renderCalendar();
}

function closeEditor() {
  selectedKey = null;
  document.getElementById('editor').hidden = true;
  renderCalendar();
}

function saveEntry() {
  if (!selectedKey) { return; }
  var memo = document.getElementById('memo-input').value.trim();
  entries[selectedKey] = { color: selectedColor, memo: memo };
  storeEntries();
  document.getElementById('delete-btn').style.display = '';
  document.getElementById('editor-msg').textContent = '保存しました';
  renderCalendar();
}

function deleteEntry() {
  if (!selectedKey) { return; }
  delete entries[selectedKey];
  storeEntries();
  document.getElementById('memo-input').value = '';
  document.getElementById('delete-btn').style.display = 'none';
  document.getElementById('editor-msg').textContent = '削除しました';
  renderCalendar();
}

document.getElementById('prev-month').addEventListener('click', function () {
  viewMonth--;
  if (viewMonth < 0) { viewMonth = 11; viewYear--; }
  renderCalendar();
});
document.getElementById('next-month').addEventListener('click', function () {
  viewMonth++;
  if (viewMonth > 11) { viewMonth = 0; viewYear++; }
  renderCalendar();
});
document.getElementById('color-input').addEventListener('input', function (e) {
  setColor(e.target.value);
});
document.getElementById('save-btn').addEventListener('click', saveEntry);
document.getElementById('delete-btn').addEventListener('click', deleteEntry);
document.getElementById('close-btn').addEventListener('click', closeEditor);

buildSwatches();
renderCalendar();
"""

BASE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>chromalog | 今日の色ログ</title>
<style>{{ css|safe }}</style>
</head>
<body>
<header>
<h1>chromalog</h1>
<p>今日の色ログ ― 1日を、1色で記録する</p>
</header>
<main>
  <div class="cal-head">
    <button id="prev-month" type="button">← 前の月</button>
    <h2 id="month-label"></h2>
    <button id="next-month" type="button">次の月 →</button>
  </div>
  <div class="weekdays" aria-hidden="true">
    <span class="sun">日</span><span>月</span><span>火</span><span>水</span><span>木</span><span>金</span><span class="sat">土</span>
  </div>
  <div id="calendar" class="calendar"></div>
  <p id="summary" class="summary"></p>

  <section id="editor" class="editor" hidden>
    <h3 id="editor-date"></h3>
    <div class="editor-row">
      <input type="color" id="color-input" value="#e5484d">
      <span id="color-value"></span>
    </div>
    <div id="swatches" class="swatches"></div>
    <label class="memo-label">今日のことば
      <input type="text" id="memo-input" maxlength="60" placeholder="ひとことメモ">
    </label>
    <div class="editor-actions">
      <button id="save-btn" type="button">保存</button>
      <button id="delete-btn" type="button">削除</button>
      <button id="close-btn" type="button">閉じる</button>
      <span id="editor-msg"></span>
    </div>
  </section>

  <p class="hint">記録はこのブラウザの中（localStorage）にだけ保存されます。サーバーには送信されません。</p>
</main>
<footer>chromalog ― 今日の色ログ</footer>
<script>{{ script|safe }}</script>
</body>
</html>
"""


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "presets": len(PRESET_COLORS)})


@app.route("/")
def index():
    script = SCRIPT.replace(
        "__PRESETS_JSON__", json.dumps(PRESET_COLORS, ensure_ascii=False)
    )
    return render_template_string(BASE, css=CSS, script=script)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
