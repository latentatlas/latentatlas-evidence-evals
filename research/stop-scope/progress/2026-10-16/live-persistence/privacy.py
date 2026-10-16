"""Allowlist-export checks, not a general personal-data detector."""
import json
import re
from pathlib import Path

PRIVATE_KEYS = frozenset({
    'access_token', 'refresh_token', 'id_token', 'api_key', 'account_id',
    'user_id', 'organization_id', 'project_id', 'client_id', 'email',
    'safety_identifier', 'prompt_cache_key',
})
PATTERNS = (
    rb'/(?:Users|home)/[^/\s"\x27]+/', rb'/var[/]folders/',
    rb'(?i)authorization:\s*bearer\s+[A-Za-z0-9._-]+',
    rb'\bsk-[A-Za-z0-9_-]{20,}',
    rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
)


def object_issues(value):
    issues = []
    def walk(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                if k.lower() in PRIVATE_KEYS and v not in (None, '', {}, []):
                    issues.append(path + '.' + k)
                if k == 'encrypted_content' and v is not None and not (
                        isinstance(v, str) and re.fullmatch(r'\[opaque-replay-sha256:[0-9a-f]{64}\]', v)):
                    issues.append(path + '.encrypted_content')
                walk(v, path + '.' + k)
        elif isinstance(x, list):
            for v in x: walk(v, path + '[]')
    walk(value, '$')
    return issues


def check_tree(root):
    problems, count = [], 0
    for path in sorted(Path(root).rglob('*')):
        if path.is_symlink():
            problems.append(path.relative_to(root).as_posix() + ':symlink'); continue
        if not path.is_file() or '__pycache__' in path.parts: continue
        count += 1
        name, raw = path.relative_to(root).as_posix(), path.read_bytes()
        if any(re.search(pattern, raw) for pattern in PATTERNS):
            problems.append(name + ':private-pattern')
        if path.suffix in {'.json', '.jsonl'}:
            objects = ([json.loads(line) for line in raw.splitlines()] if path.suffix == '.jsonl'
                       else [json.loads(raw)])
            if any(object_issues(obj) for obj in objects): problems.append(name + ':private-field')
    if problems: raise ValueError('Export privacy check: ' + ', '.join(problems))
    return {'status': 'passed_selected_patterns_and_fields', 'files_scanned': count}
