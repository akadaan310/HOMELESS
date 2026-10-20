#!/usr/bin/env python3
"""Run a real software-WebGL browser; no target-hardware performance claims."""
import json,os,time,datetime,platform,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=os.getenv('WEB_TEST_URL','http://127.0.0.1:8086/')
def run():
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  started=datetime.datetime.now(datetime.timezone.utc).isoformat();build=json.load(urllib.request.urlopen(BASE+'build-manifest.json'));context=browser.new_context(viewport={'width':800,'height':520},device_scale_factor=1)
  page=context.new_page();errors=[];console=[];requests=[]
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console.append({'type':m.type,'text':m.text}) if m.type in ('warning','error') else None);page.on('request',lambda r:requests.append({'url':r.url,'method':r.method}))
  print('navigate',flush=True);page.goto(os.getenv('WEB_TEST_URL','http://127.0.0.1:8086/'),wait_until='domcontentloaded',timeout=60000);page.wait_for_function('window.HOMELESS?.scene.ready === true',timeout=90000)
  page.wait_for_function('window.HOMELESS?.scene.geoReady && window.HOMELESS?.scene.assetsReady',timeout=180000);print('renderer and assets ready',flush=True);start=page.evaluate('window.HOMELESS.scene.position');box=page.locator('#skip').bounding_box();page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2);page.wait_for_timeout(500)
  page.locator('#world').focus();page.keyboard.down('KeyW');print('input',page.evaluate('({entered:HOMELESS.scene.entered,mode:HOMELESS.scene.mode,keys:[...HOMELESS.scene.keys],dialogs:document.querySelectorAll("dialog[open]").length})'),flush=True);
  try:page.wait_for_function('Math.hypot(HOMELESS.scene.position[0]-'+str(start[0])+',HOMELESS.scene.position[2]-'+str(start[2])+') > .3',timeout=30000)
  except Exception:
   print('movement diagnostic',page.evaluate('HOMELESS.scene.lastInput'),flush=True)
  page.keyboard.up('KeyW');page.wait_for_timeout(200)
  before=page.evaluate('window.HOMELESS.scene.position');print('walk',start,before,flush=True);page.evaluate('window.HOMELESS.journal.setPosition(window.HOMELESS.scene.position)')
  page.wait_for_timeout(24000);telemetry=page.evaluate('window.HOMELESS.telemetry()');print('telemetry captured',telemetry['scene']['triangles'],flush=True)
  # Pause new frames while the compositor captures the actual rendered last frame.
  page.evaluate('window.HOMELESS.scene.app.autoRender=false');page.screenshot(path=str(ROOT/'evidence/web_play.png'),timeout=90000);print('capture saved',flush=True)
  latest=page.evaluate('window.HOMELESS.scene.position');page.evaluate('window.HOMELESS.journal.setPosition(window.HOMELESS.scene.position)');token=page.evaluate('window.HOMELESS.session.token');page.reload(wait_until='domcontentloaded');page.wait_for_function('window.HOMELESS?.scene.ready === true',timeout=60000);after=page.evaluate('window.HOMELESS.journal.state.position');page.wait_for_timeout(500);token2=page.evaluate('window.HOMELESS.session.token')
  result={'build_revision':build['revision'],'started_utc':started,'platform':platform.platform(),'browser':browser.version,'scope':'Real Chromium software WebGL2, not physical Samsung/GPU performance','errors':errors,'warnings':console,'movement_start':start,'movement_end':before,'movement_distance':sum((a-b)**2 for a,b in zip(start,before))**.5,'latest_durable_position':latest,'restored_position':after,'persistence_equal':all(abs(a-b)<.01 for a,b in zip(latest,after)),'token_resumed':token==token2,'telemetry':telemetry,'requests':requests}
  (ROOT/'evidence/web_browser.json').write_text(json.dumps(result,indent=2));browser.close();print(json.dumps({'errors':errors,'position':before,'restored':after,'telemetry':telemetry['scene']}))
  assert not errors,errors
  assert result['persistence_equal']
  assert result['movement_distance']>.2
  assert telemetry['scene']['triangles']>500
if __name__=='__main__':run()
