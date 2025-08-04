import os


def collect():
    try:
        return dict(os.environ)
    except Exception as e:
        return {"error": str(e)}
