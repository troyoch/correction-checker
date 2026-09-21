"""Offline revision gate with a trusted, caller-owned evidence registry.

The registry and authority configuration MUST NOT come from model output.
This pure function is not authentication, persistence, or a truth classifier.
All corrections must enter through this gate; direct ingest bypasses it.
"""
from copy import deepcopy
from memory_candidate import ingest


def revise(state, proposal, *, actor_user, registry, authorities, now):
    result = deepcopy(state)
    def reject(reason):
        result.setdefault('quarantine', []).append({'proposal': deepcopy(proposal), 'reason': reason})
        return result, {'accepted': False, 'reason': reason}

    evidence_id = proposal.get('evidence_ref')
    evidence = registry.get(evidence_id) if isinstance(evidence_id, str) else None
    if not evidence:
        return reject('missing_evidence')
    if evidence_id in state.get('used_evidence', []):
        return reject('replayed_evidence')
    if evidence.get('user_id') != actor_user or proposal.get('user_id') != actor_user:
        return reject('wrong_user')
    targets = [r for r in state['rows'] if r['id'] == proposal.get('target_id')]
    if len(targets) != 1 or not targets[0].get('active', True):
        return reject('invalid_target')
    target = targets[0]
    if target.get('user_id') != actor_user:
        return reject('wrong_owner')
    if any(evidence.get(k) != proposal.get(k) for k in ('target_id', 'memory_type', 'detail')):
        return reject('evidence_mismatch')
    if proposal.get('memory_type') != target['memory_type'] or not isinstance(proposal.get('detail'), str) or not proposal['detail'].strip():
        return reject('invalid_content')
    if evidence.get('previous_detail') != target['detail']:
        return reject('stale_target')
    issued, expires = evidence.get('issued_at'), evidence.get('expires_at')
    if not all(type(x) is int for x in (issued, expires, now)) or not issued <= now < expires:
        return reject('expired_or_future_evidence')
    kind = evidence.get('kind')
    if kind == 'self_preference':
        if target['memory_type'] != 'preference' or evidence.get('subject_id') != actor_user or evidence.get('source') != 'authenticated_user':
            return reject('unauthorized_preference')
    elif kind == 'external_fact':
        if target['memory_type'] != 'fact' or target.get('topic') not in authorities.get(evidence.get('source'), set()):
            return reject('unauthorized_fact_source')
    else:
        return reject('unsupported_evidence_kind')
    # Build a minimal record; ignore caller-supplied active/validated/history fields.
    incoming = {k: target[k] for k in ('user_id', 'memory_type', 'title', 'memory_key')}
    if 'topic' in target:
        incoming['topic'] = target['topic']
    incoming['detail'] = proposal['detail']
    result['rows'] = ingest(state['rows'], incoming, revision={
        'validated': True, 'target_id': target['id'], 'evidence_ref': evidence_id})
    result.setdefault('used_evidence', []).append(evidence_id)
    # Invalidate only this user's explicit memory summary, preserving its history.
    summaries = result.setdefault('memory_summaries', {})
    old_summary = summaries.pop(str(actor_user), None)
    if old_summary is not None:
        result.setdefault('summary_history', []).append({'user_id': actor_user, 'summary': old_summary, 'evidence_ref': evidence_id})
    return result, {'accepted': True, 'reason': 'authorized_exact_revision'}
