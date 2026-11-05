from html.parser import HTMLParser
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def test_governance_standard_covers_every_candidate_and_explicit_pending_state():
    program = (ROOT / "STUDY_AREA_PROGRAM.md").read_text()
    standard = (ROOT / "outputs/atlas-data-governance-and-public-value-standard.md").read_text()
    areas = json.loads((ROOT / "data/study_area_register.json").read_text())["results"]

    assert len(areas) == 16
    assert sum(area["region"] == "United States" for area in areas) == 8
    assert sum(area["region"] == "International" for area in areas) == 8
    for phrase in ("FAIR", "CARE", "privacy", "equity", "local governance", "pending"):
        assert phrase.casefold() in program.casefold()
        assert phrase.casefold() in standard.casefold()
    assert "not evidence of community approval" in standard
    assert "for these 16 candidate areas" in program
    assert "No governance gate is counted as passed" in standard


def test_deployed_page_links_auditable_governance_standard():
    page = ROOT / "dist/index.html"
    standard = ROOT / "dist/atlas-data-governance-and-public-value-standard.md"
    output_standard = ROOT / "outputs/atlas-data-governance-and-public-value-standard.md"
    html = page.read_text()
    content = standard.read_text()
    parser = LinkParser()
    parser.feed(html)

    assert standard.read_bytes() == output_standard.read_bytes()
    assert "Data governance and public value" in html
    assert "pending for all 16 candidates" in html
    assert "CARE" in html and "FAIR" in html
    assert "atlas-data-governance-and-public-value-standard.md" in parser.links
    assert "Global Indigenous Data Alliance's CARE principles" in content
    assert "UN Fundamental Principles of Official Statistics" in content
