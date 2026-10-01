"""Plan completeness and explicit environment-error classification."""
import unittest
from run_matrix import plan
from reproduce import dependency_review

class RunnerTests(unittest.TestCase):
    def test_plan_is_twenty_four_core_plus_two_timeout(self):
        cells=plan('v01')
        self.assertEqual(len(cells),26)
        self.assertEqual(len({c['run_id'] for c in cells}),26)
        for seed in (17,41):
            core=[c for c in cells if c['seed']==seed and c['schedule']!='drain_timeout']
            self.assertEqual(len(core),12)
            self.assertEqual(len({(c['arm'],c['schedule']) for c in core}),12)
        self.assertTrue(all(c['arm']=='drain_summary' for c in cells if c['schedule']=='drain_timeout'))
    def test_known_conflicts_not_silently_clean(self):
        step={'exit_code':1,'timeout':False,'stderr':
              'Checked 167 packages in 2ms\nFound 2 incompatibilities\n'
              'The package `langchain-e2b` requires `deepagents>=0.6.0,<0.7.0`, but `0.7.13` is installed\n'
              'The package `e2b` requires `wcmatch>=10.1,<11`, but `11.0` is installed\n'}
        result=dependency_review(step)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['classification'],'known_upstream_override_conflicts')
        self.assertFalse(result['full_dependency_compatibility_claimed'])
        self.assertFalse(dependency_review({**step,'stderr':step['stderr']+'The package unknown needs another\n'})['accepted'])
        self.assertFalse(dependency_review({**step,'timeout':True})['accepted'])
    def test_unexpected_error_not_accepted(self):
        self.assertFalse(dependency_review({'exit_code':1,'timeout':False,'stderr':'internal error'})['accepted'])
        self.assertFalse(dependency_review({'exit_code':None,'timeout':True,'stderr':''})['accepted'])

if __name__=='__main__':unittest.main()
