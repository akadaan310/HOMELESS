import copy
import unittest
from cop import compile_policy, PolicyError

class Admission(unittest.TestCase):
    def setUp(self):
        self.policy={'revision':1,'constitution_sha256':'e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104','clauses':[dict(id='hd_029_ride',subject='actor',when='requested',may='ride',requires={'all':['consented','seat_ready']},preserves='identity',budget=4,witness='ride_witness',verifies='ride_test')]}
    def compile(self,p=None):
        return compile_policy(p or self.policy,{'requested','consented','seat_ready','identity'},{'ride'},{'ride_witness'},{'ride_test'})
    def test_consent_and_readiness(self):
        c=self.compile(); data=dict(requested=True,consented=True,seat_ready=True,identity=True)
        self.assertEqual(c.evaluate('actor','ride',data,4)['status'],'ADMIT')
        for field in data:
            bad=dict(data); bad[field]=False
            self.assertEqual(c.evaluate('actor','ride',bad,4)['status'],'REFUSE')
        self.assertEqual(c.evaluate('actor','ride',data,5)['status'],'REFUSE')
        self.assertEqual(c.evaluate('actor','ride',data,-1)['status'],'REFUSE')
    def test_unknown_is_not_permission(self):
        p=copy.deepcopy(self.policy);p['clauses'][0]['requires']={'not':'consented'}
        self.assertEqual(self.compile(p).evaluate('actor','ride',dict(requested=True,identity=True),0)['status'],'REFUSE')
    def test_reject_unsupported_duplicate_contradictory(self):
        for field,value in [('requires','host_exec'),('budget',True),('preserves',{'not':{'all':['consented','seat_ready']}})]:
            p=copy.deepcopy(self.policy);p['clauses'][0][field]=value
            with self.assertRaises(PolicyError): self.compile(p)
        p=copy.deepcopy(self.policy);p['clauses']*=2
        with self.assertRaises(PolicyError):self.compile(p)
    def test_malformed_schema_and_inputs(self):
        for field,value in [('revision',True),('constitution_sha256',None)]:
            p=copy.deepcopy(self.policy);p[field]=value
            with self.assertRaises(PolicyError):self.compile(p)
        c=self.compile()
        for inputs in (None, [], {'requested':1}):
            self.assertEqual(c.evaluate('actor','ride',inputs,0)['status'],'REFUSE')
        self.policy['clauses'][0]['budget']=100
        self.assertEqual(c.evaluate('actor','ride',dict(requested=True,consented=True,seat_ready=True,identity=True),5)['status'],'REFUSE')
    def test_canonical_independent_compilation(self):
        p=dict(reversed(list(self.policy.items())))
        self.assertEqual(self.compile().digest,self.compile(p).digest)
        data=dict(requested=True,consented=True,seat_ready=True,identity=True)
        self.assertEqual(self.compile().evaluate('actor','ride',data,1),self.compile(p).evaluate('actor','ride',data,1))

if __name__=='__main__':unittest.main(verbosity=2)
