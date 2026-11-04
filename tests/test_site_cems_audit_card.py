import json

from scripts.build_site_cems_audit_card import build


def test_cems_audit_card_publishes_exact_count_and_download(tmp_path):
    audit = {
        "source": {
            "catalog_codes_unique": 268,
            "flood_activations_screened": 90,
            "guide": "https://example.test/official-guide",
        },
        "counts": {"intersecting_flood_aois": 0, "intersecting_products": 0},
    }
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit))
    site_path = tmp_path / "index.html"
    site_path.write_text('<main><div class="reference-grid"><article>existing</article></div></main>')
    site_audit_path = tmp_path / "atlas-cems-event-discovery-audit.json"

    rendered = build(audit_path, site_path, site_audit_path)
    assert rendered.count("GENERATED CEMS RAPID MAPPING CARD START") == 1
    assert "268 activations · 90 floods · 0/16 fixed-area AOI overlaps" in rendered
    assert 'href="atlas-cems-event-discovery-audit.json" download=' in rendered
    assert json.loads(site_audit_path.read_text()) == audit

