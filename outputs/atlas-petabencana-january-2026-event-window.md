# Jakarta event-window reference-source recheck

**Checked:** 2026-11-04 UTC  
**Scope:** PetaBencana archive response for the official 22–26 January 2026 Jakarta inundation event. This is a source-integrity screen, not a water-pixel validation study.

## Result

The official [BPBD 24 January update](https://bpbd.jakarta.go.id/berita/Wkk2MjIwSnZEdjhUcklsb3gwVkh1Zz09/update-info-terkini-genangan-24-januari-2026-s-d-pukul-08-00-wib) reports 90 affected RT and 10 inundated road segments. The [26 January update](https://bpbd.jakarta.go.id/berita/WUVyVWZ0ejhuNXRSaFNLSDl6WVNMQT09/update-info-terkini-genangan-26-januari-2026-s-d-pukul-03-00-wib) says reported inundation had receded. The [PetaBencana archive documentation](https://docs.petabencana.id/master-1/routes/flooded-area-archive) describes a historical neighborhood-state endpoint for requested dates.

I queried the archive for **2026-01-22 00:00 through 2026-01-26 03:00 WIB**. It returned five unique area IDs, but every `last_updated` timestamp was **2022-10-07**. The response SHA-256 was `b80fbf76ed846cb7111e754a296596dcfd375e3fb55421bfc7d94efd2931f3cb`. The event-specific request returned the same response hash and records as the separate 2025 and early-January 2026 windows. The January 2020 positive-control request returned 520 records, 519 with update dates in its requested window; the October 2022 control returned six records dated within its requested window.

This demonstrates that the API response is stale for this event query. The five returned neighborhoods are not usable evidence for the January 2026 flood. PetaBencana supplies reported neighborhood states rather than flood-pixel labels; even a date-matched result would still need local geometry, fixed-AOI overlap, licensing, label review, and adequate sampling.

## Reproduction

Run `python scripts/audit_petabencana_archive.py --output outputs/atlas-petabencana-archive-screen.json` with the pinned reference-audit dependencies. The machine-readable file stores all five query windows, dates, counts, and response hashes. The focused regression test includes the exact January event window. This result adds no confirmed area: eligibility remains **0/16**, with **0/8 U.S. and 0/8 international** sites enrolled; the documented score remains **60/100 provisional**.
