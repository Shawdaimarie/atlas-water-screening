# ATLAS Release Notes

## 2026-11-02 · Private demo v3

- Added private interactive synthetic fixture walkthrough, scenario presets, baseline/aggregation comparison, ranked assets, per-asset detail and CSV export.
- Added local FastAPI fixture API with health, areas, analyses and CSV export routes.
- Added API tests and owner-only hosting readback.
- Fixed aggregate field mapping and synchronized event/area/date/provenance labels.
- Explicitly excluded NASA live ingestion, actual flood observations, damage/loss inference, and production backend deployment.
- v3 synchronizes area, event, event dates, baseline dates, map captions and asset ID prefixes when switching between fixture presets.
- Owner sign-in completed; the private deployed walkthrough was exercised in-browser.
