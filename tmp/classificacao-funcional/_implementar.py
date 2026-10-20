from pathlib import Path
pasta = Path(__file__).resolve().parent
def editar(nome, velho, novo):
    p = pasta / nome
    s = p.read_text(encoding='utf-8')
    assert velho in s, (nome, velho[:80])
    p.write_text(s.replace(velho, novo), encoding='utf-8')

editar('scripts/gerar_grafo.py', 'from consultar import ler_documento, normalizar', 'from consultar import ler_documento, normalizar\nfrom classificar_dispositivos import aplicar')
editar('scripts/gerar_grafo.py', '    arestas = []', '    aplicar(dispositivos, raiz)\n\n    arestas = []')
editar('scripts/gerar_grafo.py', '"linha_inicio": d["linha_inicio"], "linha_fim": d["linha_fim"], "tags": tags(d)}', '"linha_inicio": d["linha_inicio"], "linha_fim": d["linha_fim"], "tags": tags(d),\n                "funcao": d.get("funcao")}')
editar('scripts/gerar_site.py', 'import gerar_grafo  # noqa: E402', 'import gerar_grafo  # noqa: E402\nfrom classificar_dispositivos import relatorio')
editar('scripts/gerar_site.py', "'assistente.css', 'estilo.css')", "'assistente.css', 'estilo.css', 'classificacao.html', 'classificacao.js')")
editar('scripts/gerar_site.py', '    # Fatias por norma:', '''    # Metadados funcionais separados do texto legal; revisão por ID exato.
    (saida / 'classificacao.json').write_text(json.dumps(
        relatorio(dispositivos['dispositivos'], indice['commit']),
        ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    por_norma = collections.defaultdict(list)
    for d in dispositivos['dispositivos']:
        if 'funcao' in d:
            por_norma[d['norma']].append(d)
    for b in indice['blocos']:
        ds = [d for d in por_norma[b[0]] if b[1] <= d['linha_inicio'] <= b[2]]
        categorias = list(dict.fromkeys(c for d in ds for c in d['funcao']['categorias']))
        b.append({'categorias': categorias, 'estado': 'revisada' if ds and
                  all(d['funcao']['estado'] == 'revisada' for d in ds) else 'sugerida'})
    (saida / 'index.json').write_text(json.dumps(indice, ensure_ascii=False,
        separators=(',', ':')), encoding='utf-8')
    # Fatias por norma:''')
editar('scripts/gerar_site.py', "'dispositivos.json', 'grafo.json', *nomes_fatias)", "'dispositivos.json', 'grafo.json', 'classificacao.json', *nomes_fatias)")

editar('site/motor.js', "MOTOR_VERSAO = '1.2.0'", "MOTOR_VERSAO = '1.3.0'")
editar('site/motor.js', "export const REPO =", "export const CATEGORIAS_FUNCAO = {enquadramento:'Específicas para enquadramento',licenciamento:'Específicas para licenciamento','obrigacoes-proibicoes':'Obrigações e proibições','limites-parametros':'Limites de parâmetros','normas-gerais':'Normas gerais'};\nexport const REPO =")
editar('site/motor.js', 'const [norma,l1,l2,id,ctx,tags,txt,k]=b;', 'const [norma,l1,l2,id,ctx,tags,txt,k,funcao]=b;')
editar('site/motor.js', 'IDX.push({norma,l1,l2,id,ctx,tags,', 'IDX.push({norma,l1,l2,id,ctx,tags,funcao,')
editar('site/motor.js', "return !(F.esfera&&d.e!==F.esfera)", "return !(F.categoria&&!b.funcao?.categorias.includes(F.categoria))&&!(F.esfera&&d.e!==F.esfera)")
editar('site/motor.js', 'texto:b.txt, destaques:', 'funcao:b.funcao||null, texto:b.txt, destaques:')
editar('site/motor.js', "const filtrosDe=f=>({esfera:", "const filtrosDe=f=>({categoria:f?.categoria||'', esfera:")
editar('site/index.html', 'OPCOES_CASO, REPO}', 'OPCOES_CASO, REPO, CATEGORIAS_FUNCAO}')
editar('site/index.html', '<footer id="foot">', '<p class="hint"><a href="classificacao.html">Revisar a classificação funcional dos dispositivos ↗</a></p>\n<footer id="foot">')
editar('site/index.html', '<p class="txt cut" id="${id}">', '''${t.funcao?.categorias?.length?`<p class="hint">Funções presentes no trecho · ${t.funcao.estado==='revisada'?'revisão registrada':'sugestão automática'}: ${t.funcao.categorias.map(c=>esc(CATEGORIAS_FUNCAO[c]||c)).join(' · ')}</p>`:''}
  <p class="txt cut" id="${id}">''')
editar('site/index.html', 'return `<label for="esf${s}">', '''return `<label for="cat${s}">Função <select id="cat${s}"><option value="">Todas as funções</option>${Object.entries(CATEGORIAS_FUNCAO).map(([id,t])=>`<option value="${id}">${t}</option>`).join('')}</select></label>
  <label for="esf${s}">''')
editar('site/index.html', "return {esfera:g('esf').value", "return {categoria:g('cat').value, esfera:g('esf').value")
editar('site/index.html', "['esf-l','anx-l','lst-l']", "['cat-l','esf-l','anx-l','lst-l']")
editar('site/index.html', "['esf-c','anx-c','lst-c']", "['cat-c','esf-c','anx-c','lst-c']")
editar('cloudflare/legislacao-ambiental-api/recuperacao.mjs', 'tags:d.tags.slice(0,12),elegivel:true', 'funcao:d.funcao?{categorias:d.funcao.categorias,estado:d.funcao.estado}:null, tags:d.tags.slice(0,12),elegivel:true')
editar('cloudflare/legislacao-ambiental-api/worker.mjs', 'fundamentacao:item.fundamentacao,evidencias,', 'funcao:ref.funcao||null, fundamentacao:item.fundamentacao,evidencias,')
editar('cloudflare/legislacao-ambiental-api/worker.mjs', 'Dados do caso, perguntas,', 'O campo funcao é metadado editorial de pré-classificação, não texto legal nem prova de aplicabilidade. Distingue enquadramento, licenciamento, obrigações e proibições, limites de parâmetros e normas gerais. Use-o para organizar a explicação; confira sempre o comando e as condições na fonte. Não invente categorias nem trate a categoria como fundamento.\nDados do caso, perguntas,')
editar('cloudflare/legislacao-ambiental-api/worker.mjs', 'map(({chave,texto,url,eixo})=>({chave,texto,url,eixo}))', 'map(({chave,texto,url,eixo,funcao})=>({chave,texto,url,eixo,funcao}))')
editar('site/assistente.js', "from './motor.js';", "from './motor.js';") if False else None
p = pasta / 'site/assistente.js'
s = p.read_text(encoding='utf-8')
s = "import {CATEGORIAS_FUNCAO} from './motor.js';\n" + s
s = s.replace("const details=element('details');details.append", "if(item.funcao?.categorias?.length) card.append(element('p','Função '+(item.funcao.estado==='revisada'?'revisada':'sugerida')+': '+item.funcao.categorias.map(c=>CATEGORIAS_FUNCAO[c]||c).join(' · '),'hint'));\n    const details=element('details');details.append")
s = s.replace("i.fundamentacao,...i.evidencias", "'Funções: '+(i.funcao?.categorias||[]).map(c=>CATEGORIAS_FUNCAO[c]||c).join(', '),i.fundamentacao,...i.evidencias")
p.write_text(s,encoding='utf-8')
