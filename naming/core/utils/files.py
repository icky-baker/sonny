def get_full_name(cwd: str, name: str) -> str:
    if name:
        return f"{cwd}{name}"
    return cwd
