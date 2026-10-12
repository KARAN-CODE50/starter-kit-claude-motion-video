"""Validate publishable sources without printing any potential credential values."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'out', 'raw', 'frames'}
patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
            r'AKIA[0-9A-Z]{16}', r'sk-[A-Za-z0-9_-]{20,}',
            r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
            r'ELEVENLABS_API_KEY\s*=\s*[\"\']?[A-Za-z0-9_-]{10,}']
files = []
for p in ROOT.rglob('*'):
    rel = p.relative_to(ROOT)
    if not p.is_file() or any(part in SKIP for part in rel.parts):
        continue
    if p.name.startswith('.env') and p.name != '.env.example':
        continue
    if rel.parts[0] == 'audio' and not p.name.endswith('.example.json'):
        continue
    if p.suffix in {'.pem', '.key', '.pyc'} or p.name == '.DS_Store':
        continue
    files.append(p)
errors = []
for p in files:
    rel = p.relative_to(ROOT)
    if p.stat().st_size > 10 * 1024 * 1024:
        errors.append(f'{rel}: unexpected file larger than 10 MB')
    try:
        text = p.read_text()
    except UnicodeDecodeError:
        continue
    if any(re.search(pattern, text) for pattern in patterns):
        errors.append(f'{rel}: potential credential found (value hidden)')
    if p.suffix == '.py':
        ast.parse(text, filename=str(rel))
    if p.suffix == '.json':
        json.loads(text)
example = (ROOT / '.env.example').read_text()
assert re.search(r'^ELEVENLABS_API_KEY=\s*$', example, re.M), 'Example key must be empty'
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(files)} publishable files checked; Python syntax, JSON, size and common credential patterns')
