import unittest,tempfile,threading,json,urllib.request,urllib.error,pathlib
from worldloom.server import make_server
class HTTP(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.server=make_server(port=0,db=pathlib.Path(self.tmp.name)/'db',webroot=pathlib.Path(self.tmp.name));self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.thread.join();self.server.server_close();self.server.session.close();self.tmp.cleanup()
 def call(self,path,body=None,token=None,origin=None):
  h={'Content-Type':'application/json'}
  if token:h['Authorization']='Bearer '+token
  if origin:h['Origin']=origin
  req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=h)
  try:
   with urllib.request.urlopen(req) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_session_auth_and_duplicate_cross_client(self):
  _,s=self.call('/api/session',{});self.assertFalse(s['founder']);self.assertNotEqual(s['actor'],'dark')
  q={'operation':'journey.append','event_id':'http1','payload':{'kind':'walk','position':[1,0,2]},'actor':'dark','session':'forged'}
  self.assertEqual(self.call('/api/operation',q)[0],403)
  _,a=self.call('/api/operation',q,s['token']);self.assertEqual(a['status'],'ok');self.assertEqual(self.call('/api/operation',q,s['token'])[1]['commit_id'],a['commit_id'])
  _,resumed=self.call('/api/session',{},s['token']);self.assertEqual(resumed['session'],s['session']);self.assertTrue(resumed['resumed'])
  stale={**q,'event_id':'stale-head','expected_head':'0'*64}
  self.assertEqual(self.call('/api/operation',stale,s['token'])[1]['status'],'conflict')
  self.assertEqual(self.call('/api/operation',q,s['token'],'https://example.com')[0],403)
  _,checkpoint=self.call('/api/operation',{'operation':'query','program':'purl://dark/continuity/checkpoint'},s['token'])
  self.assertTrue(checkpoint['data']['valid']);self.assertNotIn('world',checkpoint['data'])
  self.server.allowed_origins.add('https://localhost')
  self.assertEqual(self.call('/api/session',{},origin='https://localhost')[0],200)
 def test_static_traversal_and_secret_protection(self):
  self.assertIn(self.call('/%2e%2e/.runtime/db.operator-token')[0],[403,404]);self.assertEqual(self.call('/.cache/apt/archives/')[0],404)
if __name__=='__main__':unittest.main()
