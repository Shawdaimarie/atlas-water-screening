# ATLAS release/source provenance alignment audit

**Date:** 2026-11-04  
**Purpose:** verify whether the active private Site can be reproduced from the canonical private GitHub repository.

## Evidence

| Check | Result |
|---|---|
| Current published Site | Version 56; deployment `appgdep_6aeaebcca5e88191a27437915d99d473`; status `succeeded`; custom access restricted to the owner; zero external visitors. |
| Published source reference | `184b5ac7309ff69a8e33201087eab214c2890e4d`. |
| Site package record | 22 files; 1,556,480 bytes; archive SHA-256 `a49507f5332972a87559cc8454ffb8d90f57839c9304b582fafaa472939c3742`. The archive is recorded in Sites storage. |
| Repository lookup for published source SHA | GitHub connector `fetch_commit` returned “No commit found for SHA.” |
| Local checkout | `HEAD` is `f8064f83788984260b61f24902802035cc7b14e1`; 175 modified, deleted, or untracked paths. |
| Repository activity lookup | GitHub connector returned commit `9369dbe258b007db02f0818fab96926062514734` (“Test traceable evidence export metadata”) as its newest repository search result. This differs from both the local `HEAD` and Site source SHA. |
| Local Git remote access | `git fetch origin` failed because no GitHub HTTPS username credential is configured in this environment. No files or refs were changed by the failed fetch. |
| Site/repository linkage | A fresh source credential exposed the Site-linked Cloudflare Artifact repository. A clean checkout recovered the exact source commit; no credential was retained in the checkout. |
| Clean source checkout | Commit `184b5ac7309ff69a8e33201087eab214c2890e4d` checks out cleanly in `/tmp/atlas-site-source-recovery`; its 22 tracked files include `.openai/hosting.json` and 21 `dist/` files. |
| Canonical GitHub mirror | PR #3 `https://github.com/Shawdaimarie/atlas-water-screening/pull/3` adds the exact source blobs. GitHub confirms the `dist` tree `f17cd85231c41d91c5c68e392b91c5a188d8c7b9` and `.openai` tree `ed49d440300385546836829a6152e33a3f05797f` match the Site checkout exactly. CI remains in progress; PR is not merged. |
| Rebuilt package | Sites `package-site.mjs` completed from the clean source checkout; output archive `/tmp/atlas-v56-rebuilt.tar.gz`, SHA-256 `8140ae7de079f392825af39685591b7249bd2f6f95bfcb7f7443169cf425c2ce`, 165 KB. This package was generated from the verified commit; it is not asserted to be byte-identical to the stored server archive. |

## Finding and score effect

The production Site is live and its workflows were replayed successfully. I recovered the exact source commit from the Site-linked repository using a separate empty checkout; it is clean at commit `184b5ac7309ff69a8e33201087eab214c2890e4d`. All 22 tracked files match the local hosting manifest and `dist` assets byte for byte. I uploaded those exact blobs to the private GitHub repository on PR #3 (`bde6cdfa987f59f82466e4cc18b773de01806318`); the GitHub branch `dist` subtree and `.openai` subtree SHA-1 values match the clean Site checkout exactly. PR checks are running and it is not merged. Therefore canonical-main clean-checkout reproducibility remains **pending**; the 5-point criterion remains unawarded. The other two documentation/reproducibility criteria retain credit. Canonical score: **55/100 provisional**. Independent reproduction remains pending as a separate criterion.

This audit does not alter the 8+8 study-area evidence, confirmatory eligibility (**0/16**), or scientific findings.

## Repair path

1. Reconcile this local worktree against the current private repository branch without overwriting either set of changes.
2. Publish a reviewed source snapshot to the private repository and retain its exact commit SHA.
3. Rebuild the Site package from that commit, deploy the saved version, and verify that Sites reports the same source SHA and package contents.
4. Run a clean checkout from that commit and reproduce the generated study register, audit artifacts, local tests, and Site archive before restoring the 5-point criterion.

Source assets were uploaded to PR #3; the PR remains unmerged pending CI. The live production deployment was not changed.
