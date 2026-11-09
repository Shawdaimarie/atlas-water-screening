import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_local_dist_matches_the_deployed_v76_source_manifest():
    manifest = json.loads((ROOT / "outputs/atlas-v76-dist-source-alignment.json").read_text())
    dist = ROOT / "dist"
    expected = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    actual = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in dist.iterdir()
        if path.is_file() and not path.name.startswith("._")
    }

    assert manifest["site_version"] == 76
    assert manifest["site_source_commit"] == "08f4c655927720aa115ac23b9358247e48c74a4e"
    assert manifest["deployment_id"] == "appgdep_6aeb6196270c8191886d4a3b8a0f9839"
    assert manifest["sites_archive_file_count"] == 39
    assert manifest["compared_content_file_count"] == 38
    assert actual == expected
