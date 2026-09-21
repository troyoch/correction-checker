"""Experimental Ollama reference assistant; offline fixture mode by default."""
import argparse
import json
import sqlite3
import sys
import urllib.request
from contextlib import closing
from pathlib import Path

SCHEMA = 'correction-check/1'
ENDPOINT = 'http://127.0.0.1:11434/api/chat'


def observed(value, source, **raw):
    return dict(status='observed', value=value, source=source, **raw)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def local_transport(payload):
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
                                     headers={'Content-Type': 'application/json'})
    # Fixed loopback endpoint, no credentials, environment proxies, redirects or retries.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=40) as response:
        body = response.read(1048577)
    if len(body) > 1048576:
        raise ValueError('Response too large')
    return json.loads(body)


def response_text(response):
    message = response.get('message', {})
    if (response.get('done') is not True or response.get('done_reason') != 'stop'
            or message.get('role') != 'assistant' or message.get('tool_calls')
            or not isinstance(message.get('content'), str) or not message['content'].strip()):
        raise ValueError('Incomplete, unsupported or empty response')
    return message['content'].strip()


def handle(request, config, transport=None):
    if request.get('schema') != SCHEMA:
        raise ValueError('Unsupported schema')
    if config['live'] and (not config['model'] or 'cloud' in config['model'].lower()
                           or not config['local_only_confirmed']):
        raise ValueError('Live mode requires a local model and local-only server confirmation')
    if not 1 <= config['max_requests'] <= 100:
        raise ValueError('Invalid request cap')
    op = request['operation']
    reply = dict(schema=SCHEMA, status='completed',
                 mode='live-unvalidated' if config['live'] else 'offline-scripted')
    if op == 'capabilities':
        return dict(reply, isolated_test_namespace=True,
                    architecture='Reference SQLite memory with exact fixture parser; Ollama generates probe answers only',
                    restart_scope='Local adapter process and SQLite reopen only; NOT Ollama server restart',
                    supported_case='Default Friday to Tuesday schedule only')
    root = Path(request['state_dir'])
    policy = json.dumps(config, sort_keys=True)
    with closing(sqlite3.connect(root / 'ollama-reference.sqlite')) as db:
        db.execute('CREATE TABLE IF NOT EXISTS memory (namespace TEXT PRIMARY KEY, current TEXT, summary TEXT, attempts INTEGER, policy TEXT)')
        ns = request['namespace']
        row = db.execute('SELECT current, summary, attempts, policy FROM memory WHERE namespace=?', (ns,)).fetchone()
        if row and row[3] != policy:
            raise ValueError('Run policy changed; use a new run directory')
        if op == 'teach':
            if request['text'] != 'My soccer practice is on Friday.':
                raise ValueError('Unsupported fixture')
            db.execute('INSERT INTO memory VALUES (?,?,?,?,?)', (ns, 'Friday', 'Friday', 0, policy))
        elif row is None:
            raise ValueError('Namespace not taught')
        elif op == 'correct':
            if request['text'] != 'Correction: my soccer practice is now on Tuesday.':
                raise ValueError('Unsupported fixture')
            db.execute('UPDATE memory SET current=? WHERE namespace=?', ('Tuesday', ns))
            reply['observations'] = {'accepted': observed('Tuesday', 'Exact fixture parser, not model acquisition',
                                                         raw_record={'text': request['text'], 'captured': 'Tuesday'})}
        elif op == 'restart':
            reply['lifecycle'] = {'scope': 'Reference memory only; SQLite reopened by fresh adapter process',
                                  'ollama_server_restarted': False}
        elif op == 'refresh_summary':
            db.execute('UPDATE memory SET summary=current WHERE namespace=?', (ns,))
            reply['lifecycle'] = {'summary_method': 'Deterministic copy of current record, not model summarization'}
        elif op == 'probe':
            if request['question'] != 'What day is my soccer practice?':
                raise ValueError('Unsupported fixture')
            current, summary, attempts, _ = row
            if attempts >= config['max_requests']:
                raise ValueError('Request cap reached')
            context = f'Current soccer practice day: {current}. Older summary: {summary}. The current record takes precedence.'
            payload = {'model': config['model'], 'stream': False,
                       'messages': [{'role': 'system', 'content': 'Use the supplied memory. Answer with only the day, or UNKNOWN if absent.\n' + context},
                                    {'role': 'user', 'content': request['question']}],
                       'options': {'temperature': 0, 'num_predict': 64, 'num_ctx': 2048}}
            # Persist the attempt before inference. Failures retain their reservation.
            db.execute('UPDATE memory SET attempts=attempts+1 WHERE namespace=?', (ns,))
            db.commit()
            if config['live']:
                response = (transport or local_transport)(payload)
            else:
                response = {'fixture': True, 'done': True, 'done_reason': 'stop',
                            'message': {'role': 'assistant', 'content': current}}
            answer = response_text(response)
            reply.update(raw_request=payload, raw_response=response,
                         observations={
                             'storage': observed(current, 'Reopened reference SQLite row', raw_record={'current': current, 'summary': summary}),
                             'retrieval': observed(current, 'Reference selection prefers current record; inspect full context', raw_context=context),
                             'answer': observed(answer, 'Exact stripped output; no semantic grading', raw_output=response)},
                         lifecycle={'session': request['session'], 'conversation_history': [],
                                    'note': 'Every probe is stateless inference plus shared reference memory, including learning session'},
                         attempts=attempts + 1)
        else:
            raise ValueError('Unsupported operation')
        db.commit()
    return reply


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--model', default='')
    parser.add_argument('--local-only-confirmed', action='store_true',
                        help='Attest that the Ollama server has cloud disabled and the named model is local')
    parser.add_argument('--max-requests', type=int, default=5)
    config = vars(parser.parse_args())
    try:
        result = handle(json.load(sys.stdin), config)
    except Exception:
        result = dict(schema=SCHEMA, status='unavailable',
                      reason='Adapter stopped: unsupported fixture, configuration/state error, cap, or inference failure. No retry. Inspect configuration and local state.')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

