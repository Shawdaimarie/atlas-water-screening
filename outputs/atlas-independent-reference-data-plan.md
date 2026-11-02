# ATLAS independent reference data access plan

**Prepared:** 2026-11-02  
**Status:** source identified; no granule or reference-label file has been downloaded or screened.

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

Microsoft Planetary Computer exposes anonymous STAC search for its Sentinel-1 Radiometrically Terrain Corrected collection; its data-authentication documentation says SAS tokens can be obtained anonymously. A read-only STAC query for the Jakarta AOI in January 2025 returned four scene items. These are RTC radar-backscatter assets, not OPERA DSWx-S1 water-class rasters and not independent labels. They may support a separately specified SAR-method feasibility study after radiometric/terrain QA and independent validation, but they cannot be counted as equivalent OPERA water observations or used to satisfy the current coverage gate.

Primary sources: [Planetary Computer STAC API](https://planetarycomputer.microsoft.com/docs/reference/stac/), [Planetary Computer data-access tokens](https://planetarycomputer.microsoft.com/docs/concepts/sas/), and [Sentinel-1 RTC collection explorer](https://planetarycomputer.microsoft.com/explore?d=sentinel-1-rtc).

## Effect on current claims

No registered site has passed real-raster scene QA or independent label validation. The Texas technical pilot remains outside the 16 candidates and failed its minimum-date gate. This source audit identifies a credible next reference-data lead and clarifies the Earthdata account dependency; it awards no score points and does not validate the candidate sites.
