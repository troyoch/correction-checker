import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from checker import run
from ollama_adapter import handle, response_text


class OllamaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = dict(live=False, model='', local_only_confirmed=False, max_requests=5)

    def call(self, op, namespace='test', **kwargs):
        request = dict(schema='correction-check/1', operation=op, namespace=namespace,
                       state_dir=self.tmp.name, session='fresh', question='What day is my soccer practice?')
        request.update(kwargs)
        return handle(request, self.config)

    def teach(self):
        return self.call('teach', text='My soccer practice is on Friday.')

    def test_offline_correction_survives_reopen_and_refresh(self):
        with patch('ollama_adapter.local_transport', side_effect=AssertionError('Network forbidden')):
            self.teach()
            self.call('correct', text='Correction: my soccer practice is now on Tuesday.')
            self.call('restart')
            r = self.call('probe')
            self.assertEqual(r['observations']['answer']['value'], 'Tuesday')
            self.assertEqual(r['observations']['storage']['raw_record']['summary'], 'Friday')
            self.assertTrue(r['raw_response']['fixture'])
            self.call('refresh_summary')
            self.assertEqual(self.call('probe')['observations']['storage']['raw_record']['summary'], 'Tuesday')

    def test_unknown_namespace_does_not_inherit_memory(self):
        self.teach()
        with self.assertRaises(ValueError): self.call('probe', namespace='other')

    def test_unsupported_case_rejected(self):
        with self.assertRaises(ValueError): self.call('teach', text='Friday?')

    def test_policy_change_rejected(self):
        self.teach()
        self.config['max_requests'] = 10
        with self.assertRaises(ValueError): self.call('probe')

    def test_live_opt_in_and_cloud_guard(self):
        self.config.update(live=True, model='llama3.2')
        with self.assertRaises(ValueError): self.call('capabilities')
        self.config.update(local_only_confirmed=True, model='example-cloud')
        with self.assertRaises(ValueError): self.call('capabilities')

    def test_failed_transport_consumes_attempt(self):
        self.config.update(live=True, model='llama3.2', local_only_confirmed=True, max_requests=1)
        self.teach()
        with patch('ollama_adapter.local_transport', side_effect=TimeoutError) as mock:
            with self.assertRaises(TimeoutError): self.call('probe')
            with self.assertRaises(ValueError): self.call('probe')
            self.assertEqual(mock.call_count, 1)

    def test_mock_live_payload_and_exact_answer(self):
        self.config.update(live=True, model='llama3.2', local_only_confirmed=True)
        self.teach()
        response = dict(done=True, done_reason='stop', message=dict(role='assistant', content='Friday.'))
        with patch('ollama_adapter.local_transport', return_value=response) as mock:
            r = self.call('probe')
        self.assertEqual(r['observations']['answer']['value'], 'Friday.')
        payload = mock.call_args.args[0]
        self.assertFalse(payload['stream'])
        self.assertEqual(len(payload['messages']), 2)
        self.assertNotIn('Tuesday', json.dumps(payload))

    def test_truncated_and_empty_responses_rejected(self):
        for r in [dict(done=False), dict(done=True, done_reason='length', message={'role':'assistant','content':'Tuesday'}),
                  dict(done=True, done_reason='stop', message={'role':'assistant','content':''})]:
            with self.assertRaises(ValueError): response_text(r)

    def test_full_offline_checker_sequence(self):
        out = Path(self.tmp.name) / 'run'
        adapter = str(Path(__file__).with_name('ollama_adapter.py'))
        self.assertEqual(run([sys.executable, adapter], out), 'passed')
        result = json.loads((out / 'result.json').read_text())
        self.assertEqual(len(result['reports']), 5)
        restart = result['reports'][3]['transition']['lifecycle']
        self.assertFalse(restart['ollama_server_restarted'])


if __name__ == '__main__':
    unittest.main()

