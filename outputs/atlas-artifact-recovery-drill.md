# ATLAS analysis artifact recovery drill

Date: 2026-11-03  
Scope: local recovery of manifested analysis outputs only. This drill used synthetic fixture data.

## Result

The standard-library recovery utility in `scripts/recover_analysis_artifacts.py` creates an archive from files listed in a run manifest, verifies their SHA-256 hashes, restores into a new directory, and verifies the restored files again. The restore report records that source inputs were not restored.

Focused verification: **10 passed** on Python 3.12 in the pinned Bookworm container. Coverage includes backup and restore round-trip, output hash verification, rejection of changed output, rejection of recovery-metadata name collisions, rejection of an existing restore destination, and rejection of traversal and duplicate archive members.

## Reproduce

```sh
python -m pytest -q tests/test_recover_analysis_artifacts.py
```

The full pinned project suite was also run after adding the recovery tests: **118 passed**.

## Recovery boundaries

- The archive contains `run_manifest.json` and the outputs named in its hash map.
- Input datasets are referenced only through the run's existing metadata and are not backed up by this tool.
- Restore requires a new destination and does not overwrite an existing directory.
- This is local artifact recovery evidence. It does not demonstrate a production backup schedule, cloud disaster recovery, storage durability, or recovery of historical source observations.
