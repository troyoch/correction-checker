import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openai_adapter import handle, response_text

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.config=dict(live=False,model='fixture',max_requests=5,max_output_tokens=128,
                         max_input_bytes=12000,budget='0',reservation='0')
    def call(self,op,session='learning',text='Friday',**kw):
        return handle(dict(schema='correction-check/1',namespace='test',state_dir=self.tmp.name,
                           operation=op,session=session,text=text,question=text),self.config,**kw)
    def test_offline_never_uses_network_or_credentials(self):
        with patch('openai_adapter.live_transport',side_effect=AssertionError), patch('openai_adapter.os.environ',{}):
            self.call('teach');self.call('correct',text='Tuesday')
            current=self.call('probe');fresh=self.call('probe',session='fresh',text='What day?')
        self.assertEqual(current['observations']['answer']['value'],'Tuesday')
        self.assertEqual(fresh['observations']['answer']['value'],'UNKNOWN')
        self.assertEqual(fresh['lifecycle']['history_messages'],0)
        self.assertEqual(current['observations']['storage']['status'],'unavailable')
    def test_restart_not_fabricated(self):
        self.assertEqual(self.call('restart')['status'],'unavailable')
    def test_request_cap(self):
        self.config['max_requests']=1;self.call('teach')
        with self.assertRaises(ValueError): self.call('correct')
    def test_budget_and_failure_reservation(self):
        self.config.update(live=True,budget='0.10',reservation='0.10')
        def fail(payload):raise TimeoutError()
        with self.assertRaises(TimeoutError):self.call('teach',transport=fail)
        self.assertEqual(json.loads((Path(self.tmp.name)/'openai-session-state.json').read_text())['attempts'],1)
        with self.assertRaises(ValueError):self.call('teach',transport=fail)
    def test_payload_excludes_other_sessions_and_secrets(self):
        self.config.update(live=True,budget='1',reservation='.1')
        payloads=[]
        def mock(payload):
            payloads.append(payload)
            return {'status':'completed','output':[{'type':'message','role':'assistant',
                    'content':[{'type':'output_text','text':'Friday'}]}]}
        self.call('teach',transport=mock)
        self.call('probe',session='new',text='What day?',transport=mock)
        self.assertEqual(len(payloads[1]['input']),1)
        self.assertFalse(payloads[1]['store'])
        self.assertNotIn('previous_response_id',payloads[1])
    def test_incomplete_response_not_scored(self):
        with self.assertRaises(ValueError):response_text({'status':'incomplete','output':[]})
    def test_namespace_and_policy_cannot_change(self):
        self.call('teach');self.config['max_requests']=100
        with self.assertRaises(ValueError):self.call('probe')
    def test_input_cap(self):
        self.config['max_input_bytes']=5
        with self.assertRaises(ValueError):self.call('teach')

if __name__=='__main__':unittest.main()
