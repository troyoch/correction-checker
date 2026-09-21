"""Local conservative candidate, not deployed and not a semantic classifier.

Only whitespace-equivalent detail text within the same type is automatically
collapsed. Changed meaning requires explicit, externally validated revision
metadata; canonical-key or title equality alone never authorizes replacement.
"""
from copy import deepcopy
from uuid import uuid4

def fingerprint(row):
    # Preserve case, punctuation, word order, numbers, and negation deliberately.
    return row['memory_type'], ' '.join(row['detail'].split())

def ingest(rows, incoming, *, revision=None):
    result = deepcopy(rows)
    item = deepcopy(incoming)
    item['id'] = str(uuid4())
    item['active'] = True
    item.pop('superseded_by', None)
    if revision is not None:
        if revision.get('validated') is not True or not revision.get('evidence_ref'):
            raise ValueError('Revision requires validated evidence outside model-generated memory.')
        targets = [r for r in result if r['id'] == revision.get('target_id') and r.get('active', True)]
        if len(targets) != 1 or targets[0]['memory_type'] != item['memory_type']:
            raise ValueError('Revision target missing, ambiguous, inactive, or wrong type.')
        old = targets[0]
        old['active'] = False
        old['superseded_by'] = item['id']
        item['supersedes'] = old['id']
        item['revision_evidence'] = revision['evidence_ref']
        result.append(item)
        return result
    for old in result:
        if old.get('active', True) and fingerprint(old) == fingerprint(item):
            return result
    result.append(item)
    return result

def select(rows, limit=10):
    """Preserves supplied ranking; reports overflow instead of claiming completeness."""
    unique, seen = [], set()
    for row in rows:
        if not row.get('active', True):
            continue
        key = fingerprint(row)
        if key in seen:
            continue
        seen.add(key)
        unique.append(deepcopy(row))
    return {'selected': unique[:limit], 'omitted_count': max(0, len(unique) - limit)}
