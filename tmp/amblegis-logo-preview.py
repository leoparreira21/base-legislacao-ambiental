from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path.cwd()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'_biblioteca')))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}'
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width,height,theme in [(1440,1000,'light'),(1440,1000,'dark'),(390,844,'light'),(320,700,'light')]:
        page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme,reduced_motion='reduce')
        page.route('**/api',lambda r:r.fulfill(json={'endpoints':{'buscar':'Busca'}}))
        page.route('**/api/**',lambda r:r.fulfill(json={'normas':[]}))
        page.goto(url,wait_until='networkidle')
        page.get_by_role('heading',name='Biblioteca de normas').wait_for()
        info=page.locator('.brand-logo').evaluate('''el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {intrinsic:[el.naturalWidth,el.naturalHeight],display:[r.width,r.height],background:s.backgroundColor,identity:document.querySelector('.brand-identity').getBoundingClientRect().height,listTop:document.querySelector('nav[aria-label="Normas"]').getBoundingClientRect().top,overflow:document.documentElement.scrollWidth>innerWidth}}''')
        assert info['intrinsic']==[512,512] and info['display']==[64,64] and info['background']=='rgba(0, 0, 0, 0)' and not info['overflow'], info
        page.screenshot(path=str(root/f'tmp/logo-compacta-{width}-{theme}.png'))
        print(width,theme,info)
        page.close()
    browser.close()
server.shutdown()
