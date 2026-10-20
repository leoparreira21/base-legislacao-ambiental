// Requer playwright e site gerado servido em localhost:8765 (ou UI_BASE_URL).
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE,args:['--no-sandbox','--disable-dev-shm-usage']}: {})});const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let mode='success',sent;
 await page.route('https://legislacao-ambiental-api.leoparreira1007.workers.dev/**',async route=>{
  if(route.request().url().endsWith('/health'))return route.fulfill({json:{chat:true}});
  sent=route.request().postDataJSON();
  if(mode==='slow')return new Promise(resolve=>setTimeout(()=>route.fulfill({json:{itens:[],lacunas:[],commit:'a'.repeat(40)}}).catch(()=>{}).finally(resolve),2000));
  if(mode==='error')return route.fulfill({status:429,json:{erro:'Muitas perguntas em sequência. Aguarde um minuto.'}});
  return route.fulfill({json:{status:'analisado',commit:'a'.repeat(40),itens:[{chave:'resolucao-conama-430-2011#art1_par1u',classificacao:'condicionada',fundamentacao:'A incidência depende das normas específicas e das condições da operadora. <script>alert(1)</script>',verificar:['Conferir as regras da operadora.'],evidencias:[{chave:'resolucao-conama-430-2011#art1_par1u',trecho:'O lançamento indireto de efluentes no corpo receptor',fonte:{url:'https://github.com/leoparreira21/base-legislacao-ambiental/blob/'+ 'a'.repeat(40)+'/normas/resolucao-conama-430-2011.md#L1'}}],fonte:{url:'https://github.com/leoparreira21/base-legislacao-ambiental/blob/'+ 'a'.repeat(40)+'/normas/resolucao-conama-430-2011.md#L1'}}],lacunas:['Confirmar existência de regras específicas para lançamento indireto.']}});
 });
 await page.goto((process.env.UI_BASE_URL||'http://localhost:8765')+'/assistente.html');await page.screenshot({path:'/tmp/assistente-desktop.png',fullPage:true});
 await page.locator('#send').click();if(await page.locator('#atividade').getAttribute('aria-invalid')!=='true')throw Error('validation');
 await page.locator('[data-example=saude]').click();await page.locator('#send').click();await page.locator('.evidence-card').waitFor();
 if(sent.campos.agua!=='rede'||sent.cnaes[0]!=='8630-5/02')throw Error('case');
 await page.locator('.evidence-card summary').click();if(await page.locator('#messages script').count())throw Error('XSS');
 await page.screenshot({path:'/tmp/assistente-resposta.png',fullPage:true});
 mode='error';await page.locator('#pergunta').fill('E os resíduos?');await page.locator('#send').click();await page.locator('#chat-error').waitFor({state:'visible'});if(await page.locator('#pergunta').inputValue()!=='E os resíduos?')throw Error('lost input');
 mode='slow';await page.locator('#send').click();await page.locator('#cancel').click();await page.waitForTimeout(2200);if(await page.locator('.turn').count()!==1)throw Error('stale response');
 await page.locator('#new-case').click();if(await page.locator('.turn').count())throw Error('reset');await page.locator('#undo-case').click();if(await page.locator('.turn').count()!==1)throw Error('undo');
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'/tmp/assistente-mobile.png',fullPage:true});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('horizontal overflow');
 await page.goto((process.env.UI_BASE_URL||'http://localhost:8765')+'/index.html');await page.locator('#tab-caso').click();if(!await page.locator('#p-livre').isHidden())throw Error('hidden panel');await page.locator('#tab-caso').press('ArrowLeft');if(!await page.locator('#p-caso').isHidden())throw Error('tabs');
 await browser.close();if(errors.length)throw Error(errors.join('\n'));console.log('UI OK: desktop, mobile 390px, validation, success, citations, XSS, 429, cancellation, stale response, reset/undo, keyboard tabs.');
})().catch(e=>{console.error(e);process.exit(1)});
