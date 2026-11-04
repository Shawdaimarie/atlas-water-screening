# ATLAS release/source provenance alignment audit

**Date:** 2026-11-04  
**Purpose:** verify whether the active private Site can be reproduced from the canonical private GitHub repository.

## Evidence

| Check | Result |
|---|---|
| Current published Site | Version 56; deployment `appgdep_6aeaebcca5e88191a27437915d99d473`; status `succeeded`; custom access restricted to the owner; zero external visitors. |
| Published source reference | `184b5ac7309ff69a8e33201087eab214c2890e4d`. |
| Site package record | 22 files; 1,556,480 bytes; archive SHA-256 `a49507f5332972a87559cc8454ffb8d90f57839c9304b582fafaa472939c3742`. The archive is recorded in Sites storage. |
| Initial repository lookup for published source SHA | GitHub did not contain the Site source commit when the audit began. The exact source was subsequently recovered from the Site-linked repository. |
| Local checkout | `HEAD` is `f8064f83788984260b61f24902802035cc7b14e1`; 175 modified, deleted, or untracked paths. |
| Canonical GitHub main | Commit `8014d08be673c3ecc9501d7fcd1a36022e4695e5` is current main; its `dist` subtree `f17cd85231c41d91c5c68e392b91c5a188d8c7b9` and `.openai` subtree `ed49d440300385546836829a6152e33a3f05797f` exactly match the recovered Site source checkout. |
| Local Git remote access | `git fetch origin` failed because no GitHub HTTPS username credential is configured in this environment. No files or refs were changed by the failed fetch. |
| Site/repository linkage | A fresh source credential exposed the Site-linked Cloudflare Artifact repository. A clean checkout recovered the exact source commit; no credential was retained in the checkout. |
| Clean source checkout | Commit `184b5ac7309ff69a8e33201087eab214c2890e4d` checks out cleanly in `/tmp/atlas-site-source-recovery`; its 22 tracked files include `.openai/hosting.json` and 21 `dist/` files. |
| Canonical GitHub mirror | PR #3 is merged to main as `8014d08be673c3ecc9501d7fcd1a36022e4695e5`. Its `dist` tree `f17cd85231c41d91c5c68e392b91c5a188d8c7b9` and `.openai` tree `ed49d440300385546836829a6152e33a3f05797f` match the clean Site checkout exactly. PR-head CI passed. |
| Rebuilt package | Sites `package-site.mjs` completed from the clean source checkout; output archive `/tmp/atlas-v56-rebuilt.tar.gz`, SHA-256 `8140ae7de079f392825af39685591b7249bd2f6f95bfcb7f7443169cf425c2ce`, 165 KB. This package was generated from the verified commit; it is not asserted to be byte-identical to the stored server archive. |

## Finding and score effect

The production Site is live and its workflows were replayed successfully. I recovered the exact source commit from the Site-linked repository using a separate empty checkout; it is clean at commit `184b5ac7309ff69a8e33201087eab214c2890e4d`. All 22 tracked files match the canonical main `dist` and `.openai` trees byte for byte. GitHub PR #3 merged as `8014d08be673c3ecc9501d7fcd1a36022e4695e5`; its CI passed 157 tests, the 16-area GEOID-Flood screen, container build, 11/11 HTTP smoke, runtime image audit, and dependency scan. The 5-point exact-source clean-checkout criterion is restored. The updated score is **60/100 provisional**; independent reproduction remains pending as a separate criterion.

This audit does not alter the 8+8 study-area evidence, confirmatory eligibility (**0/16**), or scientific findings.

## Repair path

Source synchronization is complete for the active static Site assets and the current project worktree snapshot. The rebuilt package came from the verified Site source commit; the live v56 deployment remains unchanged. Continue the separate research, usability, cloud, scalability, and independent-reproduction gates.

Source and current project files were uploaded by PR #3 and merged. The live production deployment was not changed.
