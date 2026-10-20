import unittest,tempfile,pathlib,time,subprocess,sys,os
from worldloom.protocol import request,Store
class IPC(unittest.TestCase):
 def test_real_daemon_kill_restart_and_cbor(self):
  with tempfile.TemporaryDirectory() as t:
   s=pathlib.Path(t)/'bus.sock';db=pathlib.Path(t)/'world.db'
   def launch():
    p=subprocess.Popen([sys.executable,'-m','worldloom.cli','daemon','--socket',str(s),'--db',str(db)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    for _ in range(100):
     try:
      request(s,{'operation':'HELLO'});return p
     except (OSError,ValueError):time.sleep(.02)
    p.kill();raise AssertionError(p.stderr.read().decode())
   p=launch()
   try:
    token=db.with_suffix('.operator-token').read_text().strip()
    q={'operation':'commit','event_id':'real-ipc','session':'test','actor':'dark','capability':token,'payload':{'kind':'sign.rename','object':'haven','text':'Rendezvous'}}
    a=request(s,q);self.assertEqual(a['status'],'ok');before=request(s,{'operation':'SNAPSHOT'})['data']
    p.kill();p.wait();p.stderr.close();s.unlink(missing_ok=True);p=launch()
    self.assertEqual(request(s,{'operation':'SNAPSHOT'})['data'],before)
    self.assertEqual(request(s,q)['commit_id'],a['commit_id'])
    self.assertEqual(request(s,{'operation':'query'})['data']['objects']['haven']['text'],'Rendezvous')
   finally:p.terminate();p.wait();p.stderr.close()
if __name__=='__main__':unittest.main()
