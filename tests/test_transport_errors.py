import socket,struct,threading,tempfile,pathlib,unittest,time
from worldloom.protocol import serve,Engine,Store,request,receive
class Framing(unittest.TestCase):
 def test_invalid_frame_returns_error_then_server_still_handles_valid_request(self):
  with tempfile.TemporaryDirectory() as t:
   path=pathlib.Path(t)/'s';store=Store(pathlib.Path(t)/'db')
   # Exercise one malformed request against an actual child daemon, then ask it
   # for its manifest. This is a reliability regression for an ordinary parser error.
   import subprocess,sys
   p=subprocess.Popen([sys.executable,'-m','worldloom.cli','daemon','--socket',str(path),'--db',str(pathlib.Path(t)/'daemon.db')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   try:
    end=time.monotonic()+10
    while not path.exists() and time.monotonic()<end:time.sleep(.02)
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
     s.settimeout(3);s.connect(str(path));s.sendall(struct.pack('!I',1)+b'\x1c');r=receive(s)
     self.assertEqual(r['status'],'error')
    self.assertEqual(request(path,{'operation':'HELLO'})['status'],'ok')
   finally:p.terminate();p.wait(timeout=5);p.stderr.close();store.close()
if __name__=='__main__':unittest.main()
