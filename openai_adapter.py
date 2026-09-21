"""Experimental Responses adapter. Offline by default; no application memory access."""
import argparse
import json
import os
import sys
import urllib.request
from decimal import Decimal
from pathlib import Path

SCHEMA = 'correction-check/1'

def unavailable(reason):
    return {'status': 'unavailable', 'reason': reason}

def response_text(response):
    if response.get('status') != 'completed':
        raise ValueError('Response incomplete; not scored')
    chunks = [c['text'] for m in response.get('output', [])
              if m.get('type') == 'message' and m.get('role') == 'assistant'
              for c in m.get('content', []) if c.get('type') == 'output_text']
    if not chunks:
        raise ValueError('No output text; not scored')
    return '\n'.join(chunks).strip()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def live_transport(payload):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise ValueError('OPENAI_API_KEY missing')
    request = urllib.request.Request('https://api.openai.com/v1/responses',
        data=json.dumps(payload).encode(),
        headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'})
    # No retries or redirects; never log headers or provider error bodies.
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=40) as result:
        return json.load(result)

def handle(request, config, transport=None):
    if request.get('schema') != SCHEMA:
        raise ValueError('Unsupported schema')
    op = request['operation']
    base = {'schema': SCHEMA, 'status': 'completed'}
    if op == 'capabilities':
        return dict(base, isolated_test_namespace=True,
            architecture='Client-managed per-session transcript; no persistent assistant memory',
            mode='live' if config['live'] else 'offline-scripted',
            unsupported=['durable memory inspection', 'restart', 'refresh_summary'])
    if op in ('restart', 'refresh_summary'):
        return dict(base, **unavailable('No owned assistant backend or summary pipeline'))
    if op not in ('teach', 'correct', 'probe'):
        raise ValueError('Unsupported operation')
    path = Path(request['state_dir']) / 'openai-session-state.json'
    state = json.loads(path.read_text()) if path.exists() else {
        'namespace': request['namespace'], 'sessions': {}, 'attempts': 0}
    if state['namespace'] != request['namespace']:
        raise ValueError('Namespace mismatch')
    policy = {k: config[k] for k in ('live','model','max_requests','max_output_tokens',
                                   'max_input_bytes','budget','reservation')}
    if state.get('policy', policy) != policy:
        raise ValueError('Run policy changed; start a new isolated run')
    state['policy'] = policy
    messages = list(state['sessions'].get(request['session'], []))
    messages.append({'role':'user', 'content':request.get('question',request.get('text'))})
    payload = {'model':config['model'], 'store':False, 'input':list(messages),
        'max_output_tokens':config['max_output_tokens'],
        'instructions':'Answer with only the requested value when known. If unknown, answer UNKNOWN.'}
    if len(json.dumps(payload,ensure_ascii=False).encode()) > config['max_input_bytes']:
        raise ValueError('Input byte cap exceeded')
    if state['attempts'] >= config['max_requests']:
        raise ValueError('Request cap exhausted')
    if Decimal(str(config['reservation'])) * (state['attempts']+1) > Decimal(str(config['budget'])):
        raise ValueError('Reservation budget exhausted')
    # Reserve BEFORE network. Failed/uncertain calls retain their full reservation.
    state['attempts'] += 1
    path.write_text(json.dumps(state),encoding='utf-8')
    if config['live']:
        response = (transport or live_transport)(payload)
    else:
        # Deliberately scripted smoke fixture, NOT a generated/recorded AI result.
        transcript = json.dumps(messages)
        value = ('Tuesday' if 'Tuesday' in transcript else 'Friday' if 'Friday' in transcript else 'UNKNOWN')
        response = {'status':'completed','fixture':True,'output':[{'type':'message',
            'role':'assistant','content':[{'type':'output_text','text':value}]}]}
    text = response_text(response)
    messages.append({'role':'assistant','content':text})
    state['sessions'][request['session']] = messages
    path.write_text(json.dumps(state),encoding='utf-8')
    obs = {stage: unavailable('Not exposed by this API-only adapter')
           for stage in ('accepted','storage','retrieval')}
    if op == 'probe':
        obs['answer'] = {'status':'observed','value':text,'source':'Exact response text; no semantic grader',
                        'raw_output':response}
    return dict(base, observations=obs, raw_request=payload, raw_response=response,
        lifecycle={'session':request['session'], 'history_messages':len(messages)-2,
                   'fresh_session_has_no_cross_session_memory':True},
        reservation={'attempts':state['attempts'], 'reserved_usd':str(Decimal(str(config['reservation']))*state['attempts']),
                     'note':'User-supplied reservation, not measured billing or guaranteed dollar cap'},
        mode='live-unvalidated' if config['live'] else 'offline-scripted')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live',action='store_true')
    p.add_argument('--model',default='offline-fixture')
    p.add_argument('--max-requests',type=int,default=5)
    p.add_argument('--max-output-tokens',type=int,default=128)
    p.add_argument('--max-input-bytes',type=int,default=12000)
    p.add_argument('--budget',default='0')
    p.add_argument('--reservation',default='0')
    a=p.parse_args();config=vars(a)
    try:
        for k in ('max_requests','max_output_tokens','max_input_bytes'):
            if config[k] <= 0: raise ValueError('Caps must be positive')
        for k in ('budget','reservation'):
            v=Decimal(config[k])
            if not v.is_finite() or v < 0: raise ValueError('Invalid reservation settings')
        if a.live and (a.model=='offline-fixture' or Decimal(a.reservation)<=0 or Decimal(a.budget)<=0):
            raise ValueError('Live mode requires explicit model, positive budget and per-call reservation')
        reply=handle(json.load(sys.stdin),config)
    except Exception:
        # Avoid persisting provider errors which may include request data or secrets.
        reply={'schema':SCHEMA, **unavailable('Adapter stopped: invalid configuration/input, budget limit, or provider failure. No automatic retry. Inspect local state and configuration.')}
    print(json.dumps(reply))

if __name__=='__main__': main()
