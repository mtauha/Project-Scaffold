import json
import yaml
import difflib


def diff_snapshots(file1, file2, fmt="json"):
    with open(file1) as f1, open(file2) as f2:
        if file1.endswith(".yaml") or file1.endswith(".yml"):
            d1 = yaml.safe_load(f1)
        else:
            d1 = json.load(f1)
        if file2.endswith(".yaml") or file2.endswith(".yml"):
            d2 = yaml.safe_load(f2)
        else:
            d2 = json.load(f2)
    d1s = json.dumps(d1, indent=2).splitlines()
    d2s = json.dumps(d2, indent=2).splitlines()
    diff = list(difflib.unified_diff(d1s, d2s, fromfile=file1, tofile=file2))
    return "\n".join(diff)
