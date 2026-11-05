import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
builder = runpy.run_path(str(ROOT / "scripts/build_site_evidence_register_link.py"))


def test_build_site_links_and_packages_the_complete_json(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(
        '<section class="study-program-head">'
        '<button type="button" class="btn" id="downloadStudyRegister">↓ &nbsp;Download area register</button>'
        "</section>",
        encoding="utf-8",
    )
    source = tmp_path / "evidence.json"
    source.write_text(json.dumps({"schema_version": 1, "results": [{"city": "Mumbai"}]}), encoding="utf-8")

    html_path, json_path = builder["build"](tmp_path, source)
    html = html_path.read_text(encoding="utf-8")
    assert "id=\"downloadStudyRegister\"" in html
    assert 'href="atlas-study-area-evidence-register.json" download=' in html
    assert json.loads(json_path.read_text(encoding="utf-8"))["results"][0]["city"] == "Mumbai"
    csv_path = tmp_path / "dist/atlas-study-area-register.csv"
    assert csv_path.read_bytes() == (ROOT / "outputs/atlas-study-area-register.csv").read_bytes()
    assert builder["update_html"](html) == html


def test_build_site_rejects_missing_or_ambiguous_register_button():
    with pytest.raises(ValueError, match="Expected one study-area"):
        builder["update_html"]("<main>no register control</main>")
    html = builder["ACTION_GROUP"] + builder["BUTTON"]
    with pytest.raises(ValueError, match="Expected one study-area"):
        builder["update_html"](html)
