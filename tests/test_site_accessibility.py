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
