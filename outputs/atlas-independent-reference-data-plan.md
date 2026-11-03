# ATLAS independent reference data access plan

**Prepared:** 2026-11-02  
**Status:** multiple sources screened; GEOID-Flood metadata add one historical St. Louis AOI/event lead, but no source supplies qualifying, comparable event-matched labels across the 16 AOIs.

## Candidate benchmark: OPERA DSWx-S1 CalVal Database V1

NASA/JPL lists a public OPERA DSWx-S1 calibration/validation database containing classification items, a reference document, and validation results. Data.gov reports one archived granule, `OPERA_DSWx-S1_V1_CalVal_DB.zip`, about 181.6 MB, with a September 2021 temporal extent and a broad global bounding box (−160.1° to 146.3° longitude; −71° to 59.2° latitude). Its spatial envelope includes the 16 candidate cities, but that does **not** prove that any candidate has a reference label in the package.

Primary records:

- [NASA/JPL Data.gov catalog record](https://catalog.data.gov/dataset/opera-dynamic-surface-water-extent-from-sentinel-1-calval-database-version-1) — describes classification items for algorithm calibration and validation and links example notebooks.
- [PO.DAAC OPERA DSWx-S1 V1 dataset page](https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1) — documents the OPERA product, public/protected S3 prefixes, and Earthdata Login requirement for protected product files.
- [OPERA CalVal example repository](https://github.com/OPERA-Cal-Val/calval-database) — contains tools and example notebooks; archived in 2022 and its README leaves database organization/access work marked “In Progress,” so examples alone do not establish a current, reproducible label-delivery path.
- [NASA earthaccess authentication guide](https://earthaccess.readthedocs.io/en/latest/user/explanation/authenticate/) — data search is available without login, but downloading or streaming NASA DAAC data requires a free Earthdata Login account.

## Access and interpretation gates

1. Confirm the account can access PO.DAAC and retrieve the CalVal ZIP through Earthdata Login. The CMR metadata query succeeds anonymously; the corresponding granule link points to `podaac-ops-cumulus-protected`. No Earthdata credentials are configured in ATLAS, and none should be committed or sent in chat.
2. Inspect the ZIP's reference document and item manifest before analysis. Record label source, annotator, source-image sensor/date/resolution, georegistration error, label-generation process, spatial footprint, and licensing/attribution. Until those fields are verified, treat the CalVal items as a candidate reference source, not independent truth.
3. Intersect actual label footprints and dates with each fixed 25 × 25 km ATLAS AOI and prespecified events. Report per-city reference counts and missingness. The catalog's global bounding box and one-month temporal extent are not evidence of per-area coverage.
4. Freeze a label holdout before parameter tuning. Keep label-derived algorithm development cases separate from the final held-out event/site assessment. Never claim accuracy from comparison to labels that were used to tune the detector.
5. Use the same rule in every enrolled site. If the database does not supply enough spatially and temporally matched references, obtain independently governed local agency/field references or defer the site; do not substitute unvalidated CMR metadata or raw backscatter for water labels.

## Alternate archive: Sentinel-1 RTC, not a replacement label or water product

Microsoft Planetary Computer exposes anonymous STAC search for its Sentinel-1 Radiometrically Terrain Corrected collection; its data-authentication documentation says SAS tokens can be obtained anonymously. A reproducible all-area screen of `sentinel-1-rtc` over the same 2024-09-01 to 2026-11-02 period returned 55–442 scene items and 55–280 distinct metadata dates per AOI. No exact acquisition date was common to all 16 boxes; 25 of 27 represented year-month bins contained at least one scene for every area. This demonstrates archive-level SAR availability, with materially different scene counts, not comparable valid-pixel observati