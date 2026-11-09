from make import *
import re

def excluir(texts):
    i = next(i for i, t in enumerate(texts) if t.startswith('Brasília, 5 de outubro de 1988'))
    j = next(j for j, t in enumerate(texts) if j > i and t.startswith('ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS'))
    return set(range(i, j))

HEAD_MID = re.compile(r'\s(?=(?:SEÇÃO|SUBSEÇÃO|CAPÍTULO|TÍTULO)\s+[IVXLC]+\b)')

def split(t):
    # título de capítulo colado ao cabeçalho seguinte ("DO SISTEMA TRIBUTÁRIO NACIONAL SEÇÃO I")
    if t.isupper() or re.match(r'^[A-ZÀ-Ú ,\-]+\s(SEÇÃO|SUBSEÇÃO|CAPÍTULO)\s', t):
        parts = HEAD_MID.split(t)
        if len(parts) > 1:
            return parts
    return [t]

def fix(t):
    t = re.sub(r'^(?:o\s+)+(§\s*\d+)\s', r'\1º ', t)          # "o § 1" -> "§ 1º" (ordinal sobrescrito fora de lugar)
    t = re.sub(r'\b(do|no|ao|o)caput(do|deste|desta)?\b', lambda m: m.group(1) + ' caput' + (' ' + m.group(2) if m.group(2) else ''), t)
    return t

TAGS = {
    'art225': ['#meio-ambiente'], 'art225_par1_inc4': ['#eia-rima'], 'art23': ['#competencia'], 'art24': ['#competencia'],
    'art231': ['#terra-indigena'], 'art176': ['#mineracao'], 'art129_cpt_inc3': ['#ministerio-publico'],
    'art170_cpt_inc6': ['#meio-ambiente'], 'art186_cpt_inc2': ['#meio-ambiente'], 'art20': ['#uniao'], 'art26': ['#estado'],
    'art30': ['#municipio'], 'art182': ['#municipio'],
}

_estado = {'prev': ''}
def pular(t):
    # inciso III revogado do antigo art. 115, parágrafo único (texto tachado), solto depois do art. 114, § 3º
    p = _estado['prev']; _estado['prev'] = t
    return t.startswith('III - (Revogado pela Emenda Constitucional nº 24, de 1999)') and p.startswith('§ 3º Em caso de greve em atividade essencial')

def notas(rd, pr, drop):
    rv = cfg['_revog']; pa = cfg['_parcial']
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto ("Constituição", 197 páginas), enviada por Leo. Não transcritos: cabeçalho institucional, links laterais ("Vide Emenda Constitucional nº 91, de 2016" e outras, registradas no cabeçalho), links de navegação ("Ato das Disposições Constitucionais Transitórias", "Atos decorrentes do disposto no § 3º do art. 5º", "ÍNDICE TEMÁTICO", "Texto compilado") e o rodapé "Este texto não substitui o publicado no D.O.U. de 5.10.1988".',
        '',
        f'- Texto compilado: o PDF traz, tachados, {len(drop)} parágrafos com redações anteriores e textos revogados. Foram identificados pelos traços horizontais (PyMuPDF) e omitidos, conforme a regra de 06/10/2026 (só o texto em vigor).',
        f'- Dispositivos revogados: o Planalto tacha o texto e deixa a anotação "(Revogado pela ...)" sem tachado. Em {len(rv)} casos o dispositivo foi mantido só com o rótulo, o ID, `#revogado` e a anotação.',
        '- Expressões tachadas dentro de dispositivos em vigor (o Planalto tacha também trechos suprimidos por emenda ou declarados inconstitucionais, com a anotação "Vide ADI ..."): as palavras tachadas foram retiradas e o restante foi mantido. Casos: ' + '; '.join(f'"{s}"' for i, k, s, kp in pa if k == 'palavras tachadas removidas' and len(s) < 120) + '.',
        '- Estrutura: TÍTULO (`##`), CAPÍTULO (`###`), SEÇÃO (`####`) e SUBSEÇÃO (`#####`). O Ato das Disposições Constitucionais Transitórias (ADCT) fica no mesmo arquivo, depois do art. 250, sob o título `## ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS` (ID `adct`), com os IDs prefixados por `adct_` (`adct_art1`, `adct_art2_par1`) e rótulos "ADCT, Art. 1º, caput", porque a numeração dos artigos recomeça. Remissões "deste Ato" e "do Ato das Disposições Constitucionais Transitórias" levam aos IDs `adct_`; as demais remissões a artigos, também dentro do ADCT, levam ao corpo permanente.',
        '- Links internos ligam o número do artigo (`art. [[#art5|5º]]`), não o inciso ou a alínea citados.',
        '- Emendas constitucionais: nome de arquivo `emenda-constitucional-federal-N-AAAA` (padrão `tipo-esfera-numero-ano` do README; nenhuma emenda estava na base). Emenda de revisão: `emenda-constitucional-revisao-federal-N-AAAA`.',
        '- Depois do art. 114, § 3º, o PDF traz, tachado, o texto anterior do art. 115 e do seu parágrafo único, com a anotação sem tachado "(Revogado pela Emenda Constitucional nº 24, de 1999)" no inciso III. Como o art. 115 atual tem outra estrutura (redação da EC nº 45/2004), esse inciso revogado não recebeu ID.',
        '- O PDF imprime o fecho "Brasília, 5 de outubro de 1988." e as assinaturas duas vezes: depois do art. 250 e depois do art. 138 do ADCT. Transcritos uma vez, no fim.',
        '- Pontuação, espaços antes de pontuação ("nacional .") e grafias da época mantidos como publicados. Ordinais com "o" sobrescrito transcritos como "º" só nos rótulos.',
        '- Norma fora do escopo ambiental, incluída por ser citada por normas ambientais da base (arts. 23, 24, 225 e outros). Tags reduzidas ao mínimo (meio ambiente, competência, terras indígenas, mineração).',
    ]
    if any(k == 'revogação sem marcador' for i, k, s, kp in pa):
        out.append('- Revogações sem rótulo identificável no trecho tachado (omitidas): ' + '; '.join(f'"{s[:80]}…" {kp}' for i, k, s, kp in pa if k == 'revogação sem marcador') + '.')
    st = [l.split(': ', 1)[1] for l in pr.log if l.startswith('inciso sem travessão')]
    log = [l for l in pr.log if not l.startswith('inciso sem travessão')]
    if st:
        out.append(f'- Incisos publicados sem travessão depois do número romano ({len(st)} casos, quase todos em redações dadas por emendas), mantidos como no original: ' + '; '.join(f'"{x[:30]}…"' for x in st) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '. Art. 102, I, e o art. 26 do ADCT e outros saltam da alínea "j" para a "l" (alfabeto da época, sem "k").')
    return out

def assin_md(a):
    return a

cfg = {
    'json': 'cf', 'arquivo': 'constituicao-federal-1988',
    'titulo': 'Constituição da República Federativa do Brasil de 1988',
    'preambulo_re': r'^Nós, representantes',
    'niveis': {'TITULO': 2, 'CAPITULO': 3, 'SECAO': 4, 'SUBSECAO': 5},
    'adct_re': r'^ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS', 'adct_titulo': 'ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS',
    'fecho_ultimo': True, 'fix': fix, 'pular': pular, 'excluir': excluir, 'split': split,
    'ementa_md': 'Constituição da República Federativa do Brasil, promulgada pela Assembleia Nacional Constituinte em 5 de outubro de 1988 (sem ementa no original).',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Vide [[emenda-constitucional-federal-91-2016|Emenda Constitucional nº 91, de 2016]]", "Vide [[emenda-constitucional-federal-106-2020|Emenda Constitucional nº 106, de 2020]]", "Vide [[emenda-constitucional-federal-107-2020|Emenda Constitucional nº 107, de 2020]]", "(Vide [[emenda-constitucional-federal-132-2023|Emenda Constitucional nº 132, de 2023]]) Vigência" (duas vezes), "Emendas Constitucionais" e "Emendas Constitucionais de Revisão" (links do portal).',
    'fm': {
        'norma': 'Constituição Federal de 1988', 'arquivo': 'constituicao-federal-1988', 'tipo': 'constituicao', 'esfera': 'federal',
        'numero': '"s/n"', 'ano': '1988', 'data_assinatura': '1988-10-05', 'data_publicacao': '1988-10-05',
        'publicacao': 'Diário Oficial da União de 05/10/1988', 'vigencia': 'na data da promulgação',
        'orgao': 'Assembleia Nacional Constituinte',
        'ementa': '"Constituição da República Federativa do Brasil (sem ementa no original)."',
        'apelido': 'CF/88; Constituição Federal',
        'situacao': 'vigente', 'texto': 'compilado (atualizado até a mais recente emenda anotada no PDF)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF do texto compilado, 197 páginas; \\"Este texto não substitui o publicado no D.O.U. de 5.10.1988\\", enviado por Leo"',
    },
    'tags': TAGS,
    'assin_md': assin_md,
    'relacao': [
        '- Norma fora do escopo ambiental da base, incluída porque as normas ambientais remetem a ela: competências comuns e concorrentes em matéria ambiental (arts. [[#art23|23]] e [[#art24|24]]), o capítulo do meio ambiente (art. [[#art225|225]]: EIA para obra ou atividade potencialmente causadora de significativa degradação, § 1º, IV; responsabilidade penal e administrativa, § 3º), a função social da propriedade rural (art. [[#art186|186]], II), a defesa do meio ambiente na ordem econômica (art. [[#art170|170]], VI), os bens da União (art. [[#art20|20]]) e os consórcios públicos (art. [[#art241|241]]).',
        '- A [[lei-complementar-federal-140-2011|Lei Complementar nº 140/2011]] regulamenta os incisos III, VI e VII do caput e o parágrafo único do art. 23 (cooperação entre os entes na proteção ambiental).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
