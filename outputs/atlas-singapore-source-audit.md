# Singapore flood-risk source audit

**Checked:** 2026-11-04 UTC  
**Candidate screen:** Singapore, 625 km² nominal fixed box centered at 1.3521° N, 103.8198° E  
**Purpose:** evaluate current public flood-risk context for candidate-site relevance; this is not a validation-label audit.

## Official PUB evidence retained

PUB’s [List of Flood-Prone Areas in Singapore](https://www.pub.gov.sg/-/media/PUB/PDF/Flood-Management/List-of-Flood-Prone-Areas-as-at-Apr-2025.pdf) is updated as of 2 April 2025. Its table is numbered 1 through 36 and the agency defines flood-prone areas as low-lying locations with a history of flooding. The count was checked from the table itself. The PDF contains named locations, not event-specific inundation polygons, per-location event dates, or a label sample. No geocoding or intersection against the frozen ATLAS box was performed, so no in-box count is asserted.

PUB also reports a national reduction in flood-prone area from about 3,200 ha in the 1970s to less than 25 ha, and describes continued flash-flood and coastal-flood risks on its [flood-resilience page](https://www.pub.gov.sg/Public/KeyInitiatives/Flood-Resilience/About-Floods). This supports Singapore-wide management need and residual-risk research context. The historical national statistic and hotspot list do not measure satellite accuracy, local loss, or service outcomes in the ATLAS box.

## Source excluded

The data.gov.sg [Flood Prone Areas dataset page](https://gbbp.data.gov.sg/datasets?agencies=PUB%2C+Singapore%27s+national+water+agency+%28PUB%29&resultId=d_c4aed98f1533eb3a66f65dbb1a30da46) exposes a 2010–2021 hectare series. The page identifies itself as a staging site and says not to use the data except for testing. It is excluded from ATLAS evidence and calculations despite the page’s dataset-citation text. No values from its 12-row CSV were used.

## Validation assessment

- **Source verification:** official PUB PDF and agency page opened; the PDF reports 36 named locations.
- **Completeness and geometry:** the PDF list is enumerated, but lacks geospatial geometry and event-level dates. Fixed-box coverage is therefore unknown.
- **Comparability:** treat the list only as candidate relevance context; do not mix it with event-scoped labels or compare its location count with pixel-based metrics.
- **Licensing and reuse:** no explicit reuse license for the PDF list was verified in this audit. Obtain agency approval or an openly licensed, machine-readable counterpart before reproducing its location records as a dataset.
- **Conclusion:** **share with caveats** as public management-need context only. Confirmatory eligibility remains 0/16; this source adds no label, raster, or rubric points.

## Next evidence needed

Seek an agency-approved or openly licensed spatial layer with event dates and flood extents, or dated sensor/alert records that can be mapped to the fixed box. Freeze a held-out event and validation sample before reviewing outcomes. Keep the data.gov.sg staging page excluded unless an authoritative production endpoint replaces it.
