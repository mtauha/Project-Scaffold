import requests


def upload_snapshot(data, url, fmt):
    headers = {
        "Content-Type": {
            "json": "application/json",
            "yaml": "application/x-yaml",
            "txt": "text/plain",
        }.get(fmt, "application/octet-stream")
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print("Upload successful.")
    else:
        print(f"Upload failed: {response.status_code} {response.text}")
