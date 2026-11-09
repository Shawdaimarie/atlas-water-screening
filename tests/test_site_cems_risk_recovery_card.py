import json

from scripts.build_site_cems_risk_recovery_card import build


def test_cems_risk_recovery_card_and_exact_audit_download(tmp_path):
    audit = {
        "source": {
            "activation_count": 43,
            "flood_activation_count": 15,
            "documentation_url": "https://example.test/official-guide",
        },
        "study_frame": {"area_count": 16},
        "counts": {
            "areas_with_any_intersection": 0,
            "product_aoi_intersections": 0,
            "intersecting_flood_product_aois": 0,
        },
    }
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit))
    site_path = tmp_path / "index.html"
    site_path.write_text(
        '<div class="reference-grid"><!-- GENERATED CEMS RAPID MAPPING CARD END -->'
        '<article>existing</article></div>'
    )
    site_audit_path = tmp_path / "atlas-cems-risk-recovery-aoi-audit.json"
    rendered = build(audit_path, site_path, site_audit_path)
    assert rendered.count("GENERATED CEMS RISK RECOVERY CARD START") == 1
    assert "43 public activations · 15 floods · 0/16 AOI intersections" in rendered
    assert 'href="atlas-cems-risk-recovery-aoi-audit.json" download=' in rendered
    assert "does not show that flooding did not occur" in rendered
    assert json.loads(site_audit_path.read_text()) == audit


def test_card_rebuild_replaces_the_existing_managed_block(tmp_path):
    audit = {
        "source": {"activation_count": 43, "flood_activation_count": 15,
                   "documentation_url": "https://example.test/guide"},
        "study_frame": {"area_count": 16},
        "counts": {"areas_with_any_intersection": 0, "product_aoi_intersections": 0,
                   "intersecting_flood_product_aois": 0},
    }
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit))
    site_path = tmp_path / "index.html"
    site_path.write_text(
        '<div class="reference-grid"><!-- GENERATED CEMS RAPID MAPPING CARD END -->'
        '<!-- GENERATED CEMS RISK RECOVERY CARD START -->old<!-- GENERATED CEMS RISK RECOVERY CARD END -->'
        '</div>'
    )
    rendered = build(audit_path, site_path, tmp_path / "site-audit.json")
    assert "old" not in rendered
    assert rendered.count("GENERATED CEMS RISK RECOVERY CARD START") == 1
