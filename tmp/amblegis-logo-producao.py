from playwright.sync_api import sync_playwright
url='https://biblioteca-legislacao-ambiental.leoparreira1007.workers.dev/'
with sync_playwright() as p:
    b=p.chromium.launch()
    page=b.new_page(viewport={'width':390,'height':844},color_scheme='light')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url,wait_until='networkidle')
    print('Produção:',page.locator('.brand-logo').evaluate('el=>({natural:[el.naturalWidth,el.naturalHeight],display:[el.width,el.height],background:getComputedStyle(el).backgroundColor})'))
    print('API:',page.evaluate('async()=>{const r=await fetch("/api");return r.status}'))
    assert page.locator('.brand-logo').evaluate('el=>el.naturalWidth===512 && el.naturalHeight===512 && el.width===64 && el.height===64')
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    page.emulate_media(color_scheme='dark')
    assert 'brightness(0)' in page.locator('.brand-logo').evaluate('el=>getComputedStyle(el).filter')
    assert not errors,errors
    print('Logo compacta, temas, celular e JavaScript conferidos em produção.')
    b.close()
