def get_full_name(cwd: str, name: str) -> str:
    if cwd == name and name == "/":
        return "/"
    if name:
        return f"{cwd}{name}"
    return cwd
