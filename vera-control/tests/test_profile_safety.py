import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_ROOT = REPO_ROOT / "resources" / "profiles" / "VORMETRA"


def test_machine_common_has_no_placeholder_network_or_invalid_exclusion():
    common_path = PROFILE_ROOT / "machine" / "fdm_machine_common.json"
    common = json.loads(common_path.read_text(encoding="utf-8"))

    assert common["print_host"] == ""
    assert common["bed_exclude_area"] == []


def test_vendor_profile_contains_no_copied_private_ip():
    for path in PROFILE_ROOT.rglob("*.json"):
        assert "10.0.1.200" not in path.read_text(encoding="utf-8"), path
