# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as chroma

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_presets_count_and_hex():
    assert len(chroma.PRESET_COLORS) >= 24
    hexes = [p["hex"] for p in chroma.PRESET_COLORS]
    assert all(HEX_RE.match(h) for h in hexes)
    assert len(set(h.lower() for h in hexes)) == len(hexes)
    assert all(p["name"].strip() for p in chroma.PRESET_COLORS)


def test_healthz():
    c = chroma.app.test_client()
    data = c.get("/healthz").get_json()
    assert data["status"] == "ok"
    assert data["presets"] == len(chroma.PRESET_COLORS)


def test_index_ok_and_calendar():
    c = chroma.app.test_client()
    resp = c.get("/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'id="calendar"' in body
    assert 'id="summary"' in body
    assert 'id="editor"' in body
    assert 'id="color-input"' in body
    assert 'id="memo-input"' in body
    assert "chromalog" in body


def test_index_contains_all_presets():
    c = chroma.app.test_client()
    body = c.get("/").get_data(as_text=True)
    for p in chroma.PRESET_COLORS:
        assert p["hex"] in body
        assert p["name"] in body


def test_localstorage_persistence():
    c = chroma.app.test_client()
    body = c.get("/").get_data(as_text=True)
    assert "chromalog-v1" in body
    assert "localStorage" in body


def test_script_not_escaped():
    # JS が HTML エスケープされず、そのまま実行可能な形で配信されること
    c = chroma.app.test_client()
    body = c.get("/").get_data(as_text=True)
    script = body.split("<script>")[1].split("</script>")[0]
    assert "&#39;" not in script
    assert "localStorage.getItem(STORAGE_KEY)" in script
    assert "var STORAGE_KEY = 'chromalog-v1';" in script
