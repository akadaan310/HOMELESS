import copy
import math
import random
import unittest
from dark.population import allocate, Population
from dark.geo import ecef, enu, unenu
from dark.life import LifeWorld, Refusal
from dark.plates import PlateWorld

class PopulationTests(unittest.TestCase):
    def test_exact_allocation_and_stable_ties(self):
        self.assertEqual(allocate(7, {'b':'1','a':'1','c':'1'}), {'a':3,'b':2,'c':2})
        r=random.Random(20261021)
        for _ in range(100):
            n=r.randrange(10000); weights={str(i):str(r.randrange(1,100)) for i in range(12)}
            self.assertEqual(sum(allocate(n,weights).values()),n)
        for total, weights in [(-1,{'a':1}),(1,{'a':-1}),(1,{'a':0}),(True,{'a':1})]:
            with self.assertRaises(ValueError): allocate(total,weights)
    def test_ranges_realization_migration(self):
        p=Population(allocate(17,{'a':1,'b':2}), 'synthetic@1')
        ids=[p.resolve(i) for i in range(17)]
        self.assertEqual(len(set(x['id'] for x in ids)),17)
        self.assertEqual(p.realize(0),p.realize(0))
        p.migrate(0,'b'); self.assertEqual(sum(p.present_counts().values()),17)
        before=copy.deepcopy(p.__dict__)
        with self.assertRaises(ValueError): p.migrate(0,'missing')
        self.assertEqual(before,p.__dict__)
        self.assertEqual(p.counts(),dict(demographic_estimate=17, realized_identities=1, stored_histories=1, active_actors=0, visible_characters=0, voiced_characters=0))
        with self.assertRaises(ValueError): p.resolve(17)

class CoordinatesTests(unittest.TestCase):
    def test_known_axes_and_stratified_roundtrip(self):
        self.assertAlmostEqual(ecef(0,0,0)[0],6378137)
        self.assertAlmostEqual(ecef(90,0,0)[2],6356752.314245,places=5)
        r=random.Random(20261021)
        for i in range(1000):
            anchor=(-89.9+179.8*(i+.5)/1000,r.uniform(-180,180),r.uniform(-430,8849))
            target=ecef(anchor[0],anchor[1],anchor[2]+10)
            local=enu(target,anchor)
            self.assertLess(math.dist(unenu(local,anchor),target),1e-7)
            self.assertAlmostEqual(local[2],10,places=7)
        self.assertLess(math.dist(ecef(0,-180,0),ecef(0,180,0)),1e-8)
        for args in [(91,0,0),(0,181,0),(0,0,float('nan'))]:
            with self.assertRaises(ValueError): ecef(*args)

class LifeTests(unittest.TestCase):
    def test_scoped_history_replay_idempotency_and_policies(self):
        w=LifeWorld()
        for kind in ['person','car','building','tree','cup','billboard','celestial_group']:
            w.register(kind,kind,policy='curious' if kind=='person' else 'reserved')
        event=w.commit('e1','person',1,'greeting',{'person','car'})
        self.assertEqual(w.commit('e1','person',1,'greeting',{'person','car'}),event)
        self.assertEqual(w.entities['tree']['memory'],[])
        self.assertEqual(w.react('person','greeting'),'notice')
        self.assertEqual(w.react('car','greeting'),'continue')
        restored=LifeWorld.restore(w.snapshot())
        self.assertEqual(restored.snapshot(),w.snapshot())
        altered=w.snapshot(); altered['events'][0]['action']='forged'
        with self.assertRaises(Refusal): LifeWorld.restore(altered)
        altered=w.snapshot(); altered['events']=[]
        with self.assertRaises(Refusal): LifeWorld.restore(altered)
        with self.assertRaises(Refusal): w.commit('e1','person',2,'other',{'person'})
        with self.assertRaises(Refusal): w.commit('e2','unknown',2,'greeting',{'person'})
        self.assertEqual(len(w.events),1)
        w.entities['car']['budget']['max_observations']=2
        w.commit('e3','person',3,'greeting',['car','car'])
        self.assertEqual(w.entities['car']['observations'],['e1','e3'])
        before=w.snapshot()
        with self.assertRaises(Refusal): w.commit('e4','person',4,'greeting',['car','person'])
        self.assertEqual(w.snapshot(),before)

class PlateTests(unittest.TestCase):
    def fixture(self):
        return PlateWorld({'a':(0.,0.),'b':(2.,0.),'c':(10.,0.),'d':(12.,0.)}, {('a','b'),('c','d')}, {'cup':{'node':'b','position':(2.,0.),'straddling':False}})
    def test_reconnection_carriage_and_inverse(self):
        w=self.fixture(); self.assertFalse(w.reachable('a','d'))
        witness=w.rewrite(0,('c','d'),('b','c'),{'cup':{'policy':'carriage','offset':(0.,1.)}},max_displacement=2)
        self.assertTrue(w.reachable('a','c')); self.assertFalse(w.reachable('c','d'))
        self.assertEqual(w.occupants['cup']['position'],(2.,1.))
        self.assertEqual(witness['effect_flags'],['reachability','geometry'])
        w.inverse(witness)
        expected=self.fixture().snapshot(); expected['revision']=2
        self.assertEqual(w.snapshot(),expected)
        with self.assertRaises(Refusal): w.inverse(witness)
    def test_all_policies_and_atomic_refusals(self):
        w=self.fixture()
        w.rewrite(0,('c','d'),('b','c'),{'cup':{'policy':'relocation','destination':'a','authority':'fixture-operator','tick':3}},max_displacement=3)
        self.assertEqual(w.occupants['cup']['node'],'a')
        for policy in [{'policy':'refuse'},{'policy':'carriage','offset':(99.,0.)},{'policy':'relocation','destination':'missing','authority':'fixture-operator','tick':3}]:
            w=self.fixture(); before=w.snapshot()
            with self.assertRaises(Refusal): w.rewrite(0,('c','d'),('b','c'),{'cup':policy},max_displacement=3)
            self.assertEqual(before,w.snapshot())
        w=self.fixture()
        with self.assertRaises(Refusal): w.rewrite(9,('c','d'),('b','c'),{})
        with self.assertRaises(Refusal): w.rewrite(0,('c','d'),('b','c'),{})
        w.occupants['cup']['straddling']=True
        with self.assertRaises(Refusal): w.rewrite(0,('c','d'),('b','c'),{'cup':{'policy':'carriage','offset':(0,1)}})

if __name__=='__main__': unittest.main()
