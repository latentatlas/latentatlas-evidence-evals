"""Boundary is an isolated per-thread root, never a guessed caller from a path."""
from pathlib import PurePosixPath


def safe_output(root, virtual_path):
    if not isinstance(virtual_path,str) or not virtual_path.startswith("/") or "\\" in virtual_path or "\x00" in virtual_path:
        return None
    parts=PurePosixPath(virtual_path).parts[1:]
    if not parts or any(p in {".",".."} or p.startswith(".") for p in parts):
        return None
    if len(parts)==1 and (parts[0].startswith("incident-") or parts[0] in {"AGENTS.md","CLAUDE.md"}):
        return None
    target=root.joinpath(*parts)
    if any(p.is_symlink() for p in (target,*target.parents) if p==root or root in p.parents):
        return None
    resolved=target.resolve()
    return target if root.resolve() in resolved.parents else None
