# NOAA/NWS flood-location screen for U.S. ATLAS candidates

**Checked:** 2026-11-04. **Purpose:** add a reproducible official U.S. event-location discovery layer to the balanced 8+8 candidate program. It does not change the fixed candidate frame or confirmatory enrollment.

## Method

The screen joins NOAA/NCEI Storm Events bulk `details` and `locations` CSVs by year, `EPISODE_ID`, and `EVENT_ID`. It retains rows whose `EVENT_TYPE` contains “FLOOD” and whose NWS-reported location point falls inside the frozen ATLAS rectangular AOI. The event table supplies the local begin/end time and `CZ_TIMEZONE`; this audit preserves those source fields and does not convert local time to UTC. Events are deduplicated by year/episode/event ID; separate location-index points are retained.

The analysis window begins 2024-09-01. The pinned NCEI 2026 files contain flood-event records through 2026-07-31; the August–November 2026 portion of the ATLAS window is absent from this release. NCEI describes the database as NWS Storm Data for significant weather phenomena and warns that events take about three months to appear. The national dataset covers the United States and adjacent waters, so international “outside scope” results must not be read as zero events.

## Results

| Candidate AOI | Unique area-event records | Location points in AOI | Finding |
|---|---:|---:|---|
| Houston | 7 | 22 | Flood/flash-flood location reports found |
| Miami | 10 | 41 | Flood/flash-flood location reports found |
| Tampa | 2 | 8 | Flood/flash-flood location reports found |
| New Orleans | 69 | 278 | Flood/flash-flood location reports found |
| New York City | 6 | 24 | Flood/flash-flood location reports found |
| Sacramento | 34 | 137 | Flood/flash-flood location reports found |
| Atlanta | 0 | 0 | No point report found in the screened files; this is not evidence of no flooding |
| St. Louis | 8 | 22 | Flood/flash-flood location reports found |

Across the U.S. subset, 7/8 AOIs have at least one NWS flood-location point; the screen found 136 area-event pairs and 532 location points. The eight international AOIs are outside this dataset's scope. Machine-readable event IDs, source-reported times, location names, and coordinates are in [`atlas-noaa-storm-events-coverage-audit.json`](atlas-noaa-storm-events-coverage-audit.json).

## Limits and score treatment

These are NWS event-report locations, not flood polygons or water-pixel labels. Counts are not event frequencies: multiple reported locations can belong to one event, point accuracy varies, and the published record is affected by reporting practices and database lag. AOI intersections show only that a report point falls inside the fixed rectangular screen. No matching to OPERA raster QA, independent reference labels, blinded review, probability sample, or uncertainty estimate is made here. This national source does not provide a common 8+8 measure. All 16 areas remain candidates, confirmatory eligibility remains **0/16**, and the canonical score remains **60/100 provisional**.

## Reproduction

The implementation is `scripts/audit_noaa_storm_events_coverage.py`; its two focused unit tests cover event-type filtering and longitude/latitude bbox handling. Download the six source files listed in the JSON to the ignored folder `work/noaa_stormevents_2024_2026/` using their documented names, then run:

```sh
.venv/bin/python scripts/audit_noaa_storm_events_coverage.py
```

The script checks the pinned SHA-256 for every compressed CSV before parsing it. Primary sources: [NCEI Storm Events Database](https://www.ncei.noaa.gov/access/storm-events-database/search), [NCEI bulk CSV archive](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/), [Storm Data bulk CSV field guide](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/Storm-Data-Bulk-csv-Format.pdf), and [NCEI event database FAQ](https://www.ncdc.noaa.gov/stormevents/faq.jsp).
