from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request,json
url='https://biblioteca-legislacao-ambiental.leoparreira1007.workers.dev'
with sync_playwright() as p:
    b=p.chromium.launch()
    page=b.new_page(viewport={'width':1440,'height':1000},color_scheme='light')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url,wait_until='networkidle')
    print('Página:',page.url,page.title())
    for path in ['/api','/api/buscar?q=efluentes&agrupar=norma']:
        print(path,page.evaluate('async path=>{const r=await fetch(path); const d=await r.json(); return {status:r.status,keys:Object.keys(d),normas:d.normas?.length}}',path))
    logo=page.get_by_alt_text('AmbLegis Database — Legislação Ambiental · Paraná')
    assert logo.evaluate('(el)=>el.complete && el.naturalWidth===2048')
    assert page.title()=='AmbLegis Database — Biblioteca de normas'
    assert page.evaluate('getComputedStyle(document.body).backgroundColor')=='rgb(246, 247, 245)'
    page.get_by_role('textbox',name='Buscar normas').fill('6938')
    page.locator('nav[aria-label="Normas"] a').first.click()
    page.locator('iframe').wait_for()
    page.frame_locator('iframe').get_by_role('button',name='Expandir tudo').wait_for()
    page.screenshot(path=str(Path('tmp/amblegis-publicado.png').resolve()))
    assert not errors,errors
    print('Produção: logo carregada, paleta aplicada, leitor aberto e nenhum erro JavaScript.')
    b.close()
