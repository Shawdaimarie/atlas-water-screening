# ATLAS Scorecard

Updated: 2026-11-02. Scope: privately hosted synthetic walkthrough plus local fixture API. Shared blueprint v1.1 clarification applies: each criterion earns 5 points or 0/pending. Product score is separate from scientific validity, customer validation and readiness for production.

**Current score: 55/100, author-verified and provisional.** No independent reproduction has occurred. The score follows the strict 5-point criterion rule. A deployment does not make synthetic data into a historical observation and does not earn unrelated reliability or scale points.

| Category | Points | Evidence and result |
|---|---:|---|
| Functionality | 15/20 | Three bounded demo criteria pass: supported scenario/area interaction; synthetic method comparison and asset inspection; labeled CSV exports. The 5-point real pinned historical-observation workflow is pending; no real raster or event has been reproduced. |
| Reliability | 5/15 | Identical API analysis requests return identical results (test below). Recovery and restore have no qualifying evidence; the prototype has no persistent analysis store. |
| Security | 15/20 | Private Site access control (5), API input/body/host/CORS boundary checks (5), and hash-locked dependency plus secret scanning (5) pass. Production API authentication/isolation remains pending. |
| Performance | 5/10 | Local fixture API sequential p95 target (<100 ms) passed; the separate throughput/cost criterion remains pending because there is no cost model for deployed raster workloads. |
| Usability | 0/10 | The previous 4-point partial credit is removed to follow the shared rubric's 5-or-0 rule. Focused author accessibility checks do not satisfy the task-study criterion or full accessibility acceptance condition. No screen-reader or task-based user study has been run. |
| Documentation and reproducibility | 15/15 | API/operator documentation, complete evidence provenance, and clean-checkout reproduction pass. The clean checkout was verified by the author; independent reproduction has not occurred. |
| Scalability | 0/10 | No declared-load test or capacity/cost model. |
| **Total** | **55/100** | Author-run evidence; not independently reproduced. |

## Verification record

- Current v16 checks (2026-11-03): local suite **56 passed**; Python 3.12 Bookworm hash-locked rerun **56 passed**. The active owner-only Site reports successful version 16 deployment; live browser checks selected New York City and exposed two below-floor sampled quarters, switched to the synthetic quality-aware aggregate, and triggered both register and evidence exports. These remain walkthrough/fixture checks; score stays 55/100 pending scientific, user-study, cloud, capacity, and independent-reproduction criteria.

- Initial local API smoke/test snapshot: `.venv/bin/python -m pytest -q` — **7 passed** on macOS/Python 3.9, project commit `44741a7`. Superseded by the current 31-test suite and the clean-checkout run below; retained as historical evidence.
- Live local API smoke: `/api/health` returned 200 with `live_nasa_ingestion:false`; aggregate analysis returned 200 with 12 synthetic records; CSV export returned 200 with 12 records plus header.
- Browser walkthrough: method switch changed from 28.6% to 21.4% for the lead fixture asset and median changed from 7.7% to 6.8%; asset detail changed on row selection; alternate preset updated area, event, event/baseline dates, map labels and LA fixture IDs; CSV export produced a success toast.
- Hosted Site: version 16 is deployed successfully to the private owner-only production URL. It retains the proposed shared measurement, reference, sampling, and precision contract; adds the GEOID-Flood St. Louis catalog screen and the 64-sample Sentinel-1 RTC VV availability panel. The latest live replay verified the 16-area table, New York City coverage profile, synthetic method comparison, and both exports; prior full replay covered all candidate profiles, event scenario, and reset flows. This does not verify real flood classification, scientific accuracy, or Google/AWS/Azure/Oracle cl