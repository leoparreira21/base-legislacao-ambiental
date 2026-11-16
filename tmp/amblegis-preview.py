from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json
root=Path.cwd()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'_biblioteca')))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}'
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':1440,'height':1000},color_scheme='light')
    page.route('**/api',lambda r:r.fulfill(json={'endpoints':{'buscar':'Busca'}}))
    page.route('**/api/**',lambda r:r.fulfill(json={'normas':[]}))
    page.goto(url,wait_until='networkidle')
    page.get_by_role('heading',name='Biblioteca de normas').wait_for()
    page.screenshot(path=str(root/'tmp/amblegis-desktop.png'))
    print('Logo:',page.locator('.brand-logo').evaluate('(el)=>({loaded:el.complete&&el.naturalWidth>0,width:el.naturalWidth,height:el.naturalHeight})'))
    for theme in ['light','dark']:
        page.close()
        page=browser.new_page(viewport={'width':1440,'height':1000},color_scheme=theme)
        page.route('**/api',lambda r:r.fulfill(json={'endpoints':{'buscar':'Busca'}}))
        page.route('**/api/**',lambda r:r.fulfill(json={'normas':[]}))
        page.goto(url+'/#lei-federal-6938-1981',wait_until='networkidle')
        page.locator('iframe').wait_for()
        page.screenshot(path=str(root/f'tmp/amblegis-leitor-{theme}.png'))
        print(theme,page.evaluate('''()=>{const s=getComputedStyle(document.body);return {bg:s.backgroundColor,text:s.color,overflow:document.documentElement.scrollWidth>innerWidth}}'''))
    page.set_viewport_size({'width':390,'height':844})
    page.emulate_media(color_scheme='light',reduced_motion='reduce')
    page.goto(url,wait_until='networkidle')
    page.screenshot(path=str(root/'tmp/amblegis-mobile.png'))
    print('Mobile overflow:',page.evaluate('document.documentElement.scrollWidth>innerWidth'))
    browser.close()
server.shutdown()
