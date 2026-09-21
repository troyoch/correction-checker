import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from checker import assess, observations_from, overall, STAGES
class ReportingRegressions(unittest.TestCase):
    def values(self):return {s:{'status':'observed','value':'Tuesday','source':'connector'} for s in STAGES}
    def test_unavailable_reply_discards_leftovers(self):
        a=assess(observations_from({'status':'unavailable','observations':self.values()}),'Tuesday')
        self.assertEqual(set(a['checks'].values()),{'not_checked'})
    def test_missing_operation_status_does_not_pass(self):
        a=assess(observations_from({'observations':self.values()}),'Tuesday')
        self.assertNotIn('pass',a['checks'].values())
    def test_bare_connector_claim_cannot_pass_overall(self):
        a=assess(self.values(),'Tuesday')
        self.assertEqual(overall([{'assessment':a}],'completed'),'inconclusive')
        self.assertEqual(set(a['evidence'].values()),{'connector_report_only'})
    def test_completed_failure_exits_nonzero_and_missing_is_inconclusive(self):
        root=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            for mode,code,outcome in [('healthy',0,'passed'),('skip_save',1,'failed'),('stale_summary',1,'failed'),('missing_storage',2,'inconclusive')]:
                out=Path(temp)/mode
                p=subprocess.run([sys.executable,str(root/'checker.py'),'--out',str(out),'--',sys.executable,str(root/'demo_adapter.py'),mode],capture_output=True,text=True)
                self.assertEqual(p.returncode,code,p.stderr)
                self.assertEqual(json.loads((out/'result.json').read_text())['outcome'],outcome)
                lines=(out/'REPORT.md').read_text().splitlines()
                start=next(i for i,line in enumerate(lines) if line.startswith('| Checkpoint'))
                self.assertTrue(all(line.startswith('|') for line in lines[start:start+7]))
                self.assertEqual(sum(line.startswith('|') for line in lines),7)
                self.assertGreater(lines.index('## Evidence notes'),start+6)
    def test_missing_evidence_cannot_hide_known_failure(self):
        o=self.values();o['answer']['value']='Friday'
        self.assertEqual(overall([{'assessment':assess(o,'Tuesday')}],'completed'),'failed')
if __name__=='__main__':unittest.main()
