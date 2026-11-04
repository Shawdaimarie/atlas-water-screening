# 8+8 study-area evidence-link audit

**Run:** 2026-11-04  
**Source register:** `data/study_area_evidence.json`  
**Records checked:** 16 area-level primary evidence URLs

## Results

- **15/16** URLs returned a 2xx response to a direct HTTPS GET from the audit environment.
- California DWR's Sacramento source returned **HTTP 403** to the scripted client. Search indexing returned the official [DWR Flood Risk Notification](https://water.ca.gov/Programs/Flood-Management/Community-Resources/Flood-Risk) page and its relevant content. Treat this as an audit-client access restriction; it does not show that the official page is missing.
- No DNS, timeout, or other HTTP failures occurred.

The indexed DWR page reports more than 1,600 miles of State-Federal levees in the Central Valley, more than 70 overtoppings or breaches since 1983, and annual risk notices for at-risk properties across 17 counties. This is regional context: the Sacramento area record itself says those counts are not local to its fixed AOI and the page does not provide local event labels.

## Limits

This audit tests URL reachability and a single Sacramento page's indexed content. It does **not** verify every empirical statement, publication date, source completeness, local spatial overlap, independent flood truth, or customer demand. It does not change study enrollment or the score. All 16 areas remain candidates; the shared observation, independent-label, probability-sample, and precision gates still apply.

Machine-readable responses, final URLs, sampled response headers, and the limitation record are in [the JSON audit](atlas-study-area-source-link-audit-2026-11-04.json).
