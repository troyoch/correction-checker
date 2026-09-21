import unittest
from checker import assess
class Checks(unittest.TestCase):
    def observed(self,v):return {'status':'observed','value':v,'source':'test'}
    def test_missing_storage_cannot_blame_retrieval(self):
        o={s:self.observed('Tuesday') for s in ('accepted','answer')};o['retrieval']=self.observed('Friday')
        self.assertEqual(assess(o,'Tuesday')['earliest_supported_divergence'],'indeterminate')
    def test_correct_answer_does_not_hide_failed_save(self):
        o={s:self.observed('Tuesday') for s in ('accepted','retrieval','answer')};o['storage']=self.observed('Friday')
        a=assess(o,'Tuesday');self.assertEqual(a['earliest_supported_divergence'],'storage');self.assertEqual(a['checks']['answer'],'pass')
    def test_unattributed_value_is_not_evidence(self):
        a=assess({'storage':{'status':'observed','value':'Tuesday'}},'Tuesday');self.assertEqual(a['checks']['storage'],'not_checked')
    def test_no_evidence_is_not_success(self):self.assertEqual(assess({},'Tuesday')['earliest_supported_divergence'],'indeterminate')
if __name__=='__main__':unittest.main()
