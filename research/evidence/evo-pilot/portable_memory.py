"""Minimal user-scoped current-memory transport, not a full Evo backup.

Integrity hashes detect accidental modification, not forgery or source trust.
Only active selected records travel; audit history and summaries stay local.
"""
import argparse
import hashlib
import json
from pathlib import Path

FIELDS = ('id', 'memory_type', 'title', 'memory_key', 'detail')

def digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()

def export_package(state, user_id, selected_ids):
    rows = [r for r in state['rows'] if r.get('user_id') == user_id and r.get('active') is True]
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)) or not set(selected_ids).issubset(ids):
        raise ValueError('Selection must contain unique active records belonging to this user.')
    records = [{k: r[k] for k in FIELDS} for r in rows if r['id'] in selected_ids]
    payload = {'schema': 'evo-portable-memory/1', 'owner': str(user_id), 'records': records}
    package = {'payload': payload, 'sha256': digest(payload)}
    validate(package, user_id)
    return package

def validate(package, user_id):
    if not isinstance(package, dict) or set(package) != {'payload', 'sha256'}:
        raise ValueError('Invalid envelope')
    p = package['payload']
    if not isinstance(p, dict) or set(p) != {'schema', 'owner', 'records'}:
        raise ValueError('Invalid payload')
    if p['schema'] != 'evo-portable-memory/1' or p['owner'] != str(user_id):
        raise ValueError('Unsupported schema or wrong owner')
    if digest(p) != package['sha256']:
        raise ValueError('Integrity mismatch')
    if not isinstance(p['records'], list) or len(p['records']) > 1000:
        raise ValueError('Invalid record count')
    ids = set()
    for r in p['records']:
        if not isinstance(r, dict) or set(r) != set(FIELDS):
            raise ValueError('Unexpected record fields')
        if any(not isinstance(r[k], str) or not r[k].strip() or len(r[k]) > 10000 for k in FIELDS):
            raise ValueError('Invalid record text')
        if r['id'] in ids:
            raise ValueError('Duplicate record')
        ids.add(r['id'])
    return p

def restore(package, user_id):
    p = validate(package, user_id)
    return {'rows': [dict(r, user_id=user_id, active=True) for r in p['records']],
            'memory_summaries': {}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package')
    parser.add_argument('destination')
    parser.add_argument('--owner', required=True)
    args = parser.parse_args()
    source = Path(args.package)
    if source.stat().st_size > 2000000:
        raise ValueError('Package exceeds size limit')
    state = restore(json.loads(source.read_text(encoding='utf-8')), args.owner)
    # Never overwrite an existing destination or merge stale memory implicitly.
    with Path(args.destination).open('x', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
