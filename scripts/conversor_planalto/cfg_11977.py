from make import *
import json, re

NOTAS = json.load(open(f'{SP}/l11977.notas.json'))['notas']

def fix(t):
    def rep(m):
        n = m.group(1)
        return f' (Nota de rodapé {n} do original, ligada à chamada "(*)": {NOTAS[n].rstrip(")")})'
    t = re.sub(r'\(\*\)(\d)\s*$', rep, t)
    t = re.sub(r'\s{2,}', ' ', t)
    return t

def notas(rd, pr, drop):
    rem = getattr(pr, 'revogados_com_texto', [])
    log = [l for l in pr.log if not l.startswith(('texto de dispositivo revogado', 'inciso sem travessão', 'anotação '))]
    st = [l for l in pr.log if l.startswith('inciso sem travessão')]
    out = [
        'Fonte: PDF do texto atualizado da Câmara dos Deputados (Centro de Documentação e Informação, 31 páginas), enviado por Leo. O PDF não traz data de publicação nem o rodapé do DOU; o cabeçalho "CÂMARA DOS DEPUTADOS / Centro de Documentação e Informação" não foi transcrito.',
        '',
        '- Texto atualizado da Câmara: mostra só a redação em vigor, com anotações como "(“Caput” do artigo com redação dada pela Lei nº ...)", "(Inciso acrescido pela ...)", "(Artigo revogado pela ...)". Não há redações anteriores no PDF.',
        f'- Dispositivos que a Câmara publica com o texto e a anotação de revogação ("(Revogado a partir de 31/12/2011, de acordo com inciso III do art. 13 da Lei nº 12.424 ...)" e semelhantes): o texto foi retirado pela regra de 06/10/2026 (só o texto em vigor) e ficaram rótulo, ID, `#revogado` e a anotação. Casos ({len(rem)}): ' + ', '.join(f'`{i}`' for i, _ in rem) + '. O texto retirado continua no PDF da Câmara.',
        '- Notas de rodapé do original (6, chamadas "(*)1" a "(*)6" depois das anotações dos arts. 5º, 11, 12, 18 e 19): transcritas como anotação no próprio dispositivo ("Nota de rodapé N do original ..."). Elas dizem se a revogação pela Medida Provisória nº 514/2010 foi mantida pela Lei nº 12.424/2011 (revogação a partir de 31/12/2011) ou desfeita (nota 2, art. 11, parágrafo único: "mantido pela Lei nº 12.424"). A nota 2 traz "Media Provisória" (erro do original).',
        '- Arts. 74 a 79 e outros que alteram leis: as novas redações estão em citação (`art74_cpt_alt1` etc.), com as aspas e as linhas pontilhadas do original; as linhas partidas do bloco citado foram reunidas.',
        '- "Art. 69 a 71-A. (Revogados ...)": no singular no original; um ID por artigo revogado (`art69` a `art71`, `art71-a`), como nos demais intervalos ("Arts. 46 a 52", "Arts. 53 a 60-A", "Arts. 64 a 68").',
        '- A Câmara põe a anotação de inclusão ou nova redação de um artigo, parágrafo ou inciso inteiro no fim do seu último trecho ("(Artigo acrescido pela ...)" depois do último inciso). Essas anotações foram levadas ao dispositivo que nomeiam (caput do artigo, parágrafo ou inciso), para que `#incluido`/`#redacao-alterada` e o histórico fiquem no lugar certo.',
        '- Hifens de fim de linha unidos: "habite-se", "satisfazê-las".',
        '- Preâmbulo: "O VICE-PRESIDENTE DA REPÚBLICA, no exercício do cargo de PRESIDENTE DA REPÚBLICA" sai em duas linhas, com espaçamento largo; unido.',
        '- Art. 1º, § 1º, inciso II: publicado sem travessão ("II imóvel novo"); mantido.',
        '- Norma fora do escopo ambiental, incluída por ser citada por normas ambientais (a [[lei-federal-12651-2012#art3_cpt_inc9_alid|Lei nº 12.651/2012, art. 3º, IX, "d"]], remete a ela). Sem tags temáticas.',
    ]
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

def ementa():
    P = json.load(open(f'{SP}/l11977.json'))
    return ' '.join(r['t'] for r in P[3:12])

cfg = {
    'json': 'l11977', 'arquivo': 'lei-federal-11977-2009',
    'titulo': 'Lei Federal nº 11.977, de 7 de julho de 2009',
    'preambulo_re': r'^O VICE-PRESIDENTE', 'preambulo_n': 2,
    'niveis': {'CAPITULO': 2, 'SECAO': 3, 'SUBSECAO': 4},
    'fix': fix, 'revogado_remove_texto': True, 'camara': True,
    'ementa_md': ementa(),
    'fm': {
        'norma': 'Lei Federal nº 11.977/2009', 'arquivo': 'lei-federal-11977-2009', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '11977', 'ano': '2009', 'data_assinatura': '2009-07-07',
        'vigencia': 'na data da publicação (art. 83)',
        'orgao': 'Presidência da República',
        'ementa': '"' + ementa() + '"',
        'apelido': 'Lei do Programa Minha Casa, Minha Vida',
        'situacao': 'vigente', 'texto': 'compilado (texto atualizado da Câmara dos Deputados, última alteração anotada: Lei nº 15.081/2024)',
        'regulamenta': '[]', 'regulamentado_por': '[]',
        'altera': fm_list(['decreto-lei-federal-3365-1941', 'lei-federal-4380-1964', 'lei-federal-6015-1973', 'lei-federal-8036-1990', 'lei-federal-10257-2001', 'medida-provisoria-2197-43-2001']),
        'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Câmara dos Deputados – Centro de Documentação e Informação, texto atualizado em PDF, 31 páginas, enviado por Leo"',
    },
    'tags': {},
    'assinaturas': lambda a: ['JOSÉ ALENCAR GOMES DA SILVA', 'Luiz Paulo Teles Ferreira Barreto', 'Guido Mantega', 'Paulo Bernardo Silva', 'Carlos Minc', 'Márcio Fortes de Almeida'],
    'relacao': [
        '- Fora do escopo ambiental da base. O Capítulo III (regularização fundiária de assentamentos urbanos, arts. 46 a 71-A) foi revogado pela [[lei-federal-13465-2017|Lei nº 13.465/2017]], que hoje rege a regularização fundiária urbana (Reurb). A [[lei-federal-12651-2012#art3_cpt_inc9_alid|Lei nº 12.651/2012, art. 3º, IX, "d"]] ainda remete a esta Lei para a regularização fundiária de assentamentos de baixa renda em áreas urbanas consolidadas; na prática, a regularização segue hoje a Lei nº 13.465/2017 (Reurb) (informação do conversor, não está no PDF).',
        '- O art. 1º, § 1º, inciso V, define agricultor familiar por remissão ao art. 3º da [[lei-federal-11326-2006#art3|Lei nº 11.326/2006]].',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
