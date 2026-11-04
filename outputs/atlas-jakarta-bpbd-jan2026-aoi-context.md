# Jakarta January 2026 official-event/AOI context screen

Updated: 2026-11-04 UTC. This is an event-location context screen for the fixed Jakarta candidate box; it is not a flood-water map or an independent reference-label audit.

## Finding

BPBD DKI Jakarta reported that heavy rain beginning 22 January 2026 caused inundation. Its 24 January 08:00 WIB update counted 90 affected RT and 10 inundated road segments across Jakarta Barat, Jakarta Selatan, Jakarta Timur, and Jakarta Utara. A 26 January 03:00 WIB update said all recorded inundation had receded. The two reports bound the official event context to 22–26 January; the 24 January bulletin is the time-stamped impact snapshot.

The fixed 25 × 25 km Jakarta AOI is `106.732649,-6.321089,106.958551,-6.096511`. An exact geometry overlay found that **20 of the 21 kelurahan polygons named in BPBD's 24 January impact list positively intersect the fixed box**. Duri Kosambi was not returned by the AOI intersection query. This establishes that most of the event's reported administrative areas overlap the candidate box, but BPBD does not locate each affected RT or road within the overlapping portions of those polygons.

The overlap therefore supports Jakarta as an event-screening candidate only. It does not prove that inundation occurred inside the fixed AOI, supply a pixel reference label, establish OPERA pixel quality, or pass confirmatory enrollment. The event remains exploratory.

## Sources and method

- BPBD DKI, [24 January 2026 inundation report, 08:00 WIB](https://bpbd.jakarta.go.id/berita/Wkk2MjIwSnZEdjhUcklsb3gwVkh1Zz09/update-info-terkini-genangan-24-januari-2026-s-d-pukul-08-00-wib): onset attribution, 90 RT, 10 roads, and named affected kelurahan.
- BPBD DKI, [26 January 2026 inundation update, 03:00 WIB](https://bpbd.jakarta.go.id/berita/WUVyVWZ0ejhuNXRSaFNLSDl6WVNMQT09/update-info-terkini-genangan-26-januari-2026-s-d-pukul-03-00-wib): all reported inundation had receded.
- DKI Jakarta DPMPTSP GIS, [Kelurahan administration FeatureServer](https://gis-dpmptsp.jakarta.go.id/arcgis/rest/services/Hosted/Batas_Administrasi_Kelurahan_DKI_Jakarta/FeatureServer), layer 85, item `b5502a02bdad4964a81eb93a1fb03597`. The query requested intersecting boundary features in WGS84 for the registered AOI and matched each official report name together with its administrative city. Returned polygon geometry was intersected locally; positive planar area was used only to distinguish a real polygon overlap from boundary-only contact. Degree-squared values are not interpreted as land area.
- The live geometry query returned 246 boundary features. Its response SHA-256 is `1d63c42d7990b91e3af776bef3307659e1762a90cc1149117f676a93a1241d3f`.

The official reports list conditions at administrative-unit level. A kelurahan polygon may extend well beyond the AOI; polygon overlap is not a claim that the event's inundated locations were within that intersection. The one non-returned area is not evidence that flooding did not occur there.

## Observation opportunity and open validation gates

The common OPERA DSWx-S1 metadata register has dates near this event on 18, 21, 23, 25, 26, and 30 January 2026. These are archive metadata dates only. No January 2026 raster was retrieved or passed through the BWTR pixel QA gate for this audit. No independently licensed pixel labels, event-point geometries, asset-footprint review, probability sample, or precision assessment is attached. The complete comparable-study enrollment rule remains unmet for Jakarta and all other candidates.

Next evidence needed: obtain point- or neighborhood-level event locations that can be intersected with the fixed AOI; inspect all event/baseline BWTR rasters under the shared QA rule; secure reuse terms; and create independent, blinded pixel reference labels with probability sampling. Until then, retain the 8+8 candidate status and award no score credit.

## Reproduction and machine-readable record

Run `python scripts/audit_jakarta_bpb_event_spatial_context.py` after installing the pinned `requirements-reference-audit.lock` in Python 3.12. The output is [`atlas-jakarta-bpbd-jan2026-aoi-context.json`](atlas-jakarta-bpbd-jan2026-aoi-context.json); the script and two fixture tests are in `scripts/audit_jakarta_bpb_event_spatial_context.py` and `tests/test_jakarta_bpb_event_spatial_context.py`.

**Result:** 20/21 named administrative areas overlap the box; precise inundation inside the box is not verified; pixel QA and independent labels are absent; confirmatory eligibility is false; rubric score credit is zero.
