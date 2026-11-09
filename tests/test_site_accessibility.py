from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in channels]
    return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_site_small_text_contrast_for_accessibility_statuses():
    site = (ROOT / "dist/index.html").read_text()
    assert ".pill.warn{background:#f7eddf;color:#875c29}" in site
    assert ".detail-head span{margin-left:auto;color:#0e6b5e" in site
    assert ".rtc-table tbody th small{display:block;color:#596861" in site
    assert contrast_ratio("#875c29", "#f7eddf") >= 4.5
    assert contrast_ratio("#0e6b5e", "#f7f9f7") >= 4.5
    assert contrast_ratio("#596861", "#ffffff") >= 4.5


def test_site_has_a_keyboard_skip_link_and_minimum_content_link_targets():
    site = (ROOT / "dist/index.html").read_text()
    assert '<a class="skip-link" href="#mainContent">Skip to main content</a>' in site
    assert '<main class="main" id="mainContent" tabindex="-1">' in site
    assert ".skip-link:focus{top:12px}" in site
    assert "a:not(.skip-link){display:inline-block;min-height:24px;line-height:1.4;padding:3px 2px}" in site


def test_site_small_text_override_meets_wcag_aa_on_light_surfaces():
    site = (ROOT / "dist/index.html").read_text()
    assert (
        ".subhead,.stat-label,.stat-note,.stat-value small,.panel-head span,"
        ".map-caption,.event-card small,.aside-foot,.analysis p,.method-desc,.tab,"
        ".rank-head,.asset-name small,.detail-grid label,.trace-row label,.note,.footer,"
        ".study-program-head p,.study-foot,.study-area-button span,.study-metric span"
        "{color:#596861!important}"
    ) in site
    for background in ("#ffffff", "#f4f6f2", "#f4f7f4"):
        assert contrast_ratio("#596861", background) >= 4.5


def test_site_interactive_control_boundaries_meet_wcag_nontext_contrast():
    site = (ROOT / "dist/index.html").read_text()
    assert ".select{width:100%;padding:11px 12px;border:1px solid #7f8c84;" in site
    assert ".btn{border:1px solid #7f8c84;" in site
    assert ".study-area-button{min-height:44px;border:1px solid #7f8c84;" in site
    assert ".tab.active{background:#e8f3ef;color:#176f61;border-color:#0e6b5e;" in site
    assert ".study-area-button:hover,.study-area-button.active{border-color:#0e6b5e;" in site
    assert contrast_ratio("#7f8c84", "#ffffff") >= 3
    assert contrast_ratio("#0e6b5e", "#eef7f4") >= 3
    assert contrast_ratio("#0e6b5e", "#e8f3ef") >= 3


def test_schematic_map_labels_meet_wcag_aa_contrast():
    site = (ROOT / "dist/index.html").read_text()
    assert 'id="mapAreaLabel" x="297" y="90" font-size="10" fill="#596861"' in site
    assert 'id="mapCorridorLabel" x="91" y="164" font-size="9" fill="#596861"' in site
    assert contrast_ratio("#596861", "#e8eee9") >= 4.5
