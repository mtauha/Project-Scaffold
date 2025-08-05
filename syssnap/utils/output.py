import json
import yaml


def write_output(data, fmt="json", out=None, as_bytes=False):
    if fmt == "json":
        s = json.dumps(data, indent=2)
        b = s.encode("utf-8")
    elif fmt == "yaml":
        s = yaml.dump(data)
        b = s.encode("utf-8")
    else:
        s = str(data)
        b = s.encode("utf-8")
    if out:
        with open(out, "wb") as f:
            f.write(b)
    else:
        print(s)
    return b if as_bytes else s
