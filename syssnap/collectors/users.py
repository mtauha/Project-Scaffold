def collect():
    users = {}
    try:
        # List all users
        with open("/etc/passwd") as f:
            users["passwd"] = f.read()
        # List all groups
        with open("/etc/group") as f:
            users["group"] = f.read()
        # Sudoers
        try:
            with open("/etc/sudoers") as f:
                users["sudoers"] = f.read()
        except Exception:
            users["sudoers"] = "N/A"
    except Exception as e:
        users["error"] = str(e)
    return users
