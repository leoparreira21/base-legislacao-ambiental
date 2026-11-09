from make import *
import re

LAY = open(f'{SP}/pdf/l8847.lay.txt', encoding='utf-8').read()

def tabelas():
    tabs = []
    cur = None
    for ln in LAY.splitlines():
        m = re.match(r'^\s*TABELA (I+): (.*)$', ln)
        if m:
            cur = [m.group(1), m.group(2).strip(), []]; tabs.append(cur); continue
        if cur and re.match(r'^\s+E SUL MATOGROSSENSE', ln):
            cur[1] += ' E SUL MATOGROSSENSE'; continue
        m = re.match(r'^\s*(Até \d+|\d+ a \d+|Acima de \d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$', ln)
        if m and cur:
            cur[2].append(m.groups())
    return tabs

COLS = ['>80', '>65 A 80', '>50 A 65', '>30 A 50', '0 A 30']

def anexo(rd, rest):
    out = ['## ANEXO I {#anexo1}', '']
    for num, tit, rows in tabelas():
        n = len(num)
        out.append(f'#### TABELA {num}: {tit} {{#anexo1_tab{n}}}')
        out.append('')
        for i, r in enumerate(rows, 1):
            cells = [f'TAMANHO HECTARES: {r[0]}'] + [f'UTILIZAÇÃO EFETIVA DA ÁREA APROVEITÁVEL % — {c}: {v}' for c, v in zip(COLS, r[1:])]
            out.append(f'- **Anexo I, Tabela {num}, linha {i}** {{#anexo1_tab{n}_lin{i}}} #itr ' + ' | '.join(cells))
        out.append('')
        assert len(rows) == 12, (num, len(rows))
    out.append('---')
    out.append('')
    return out

def notas(rd, pr, drop):
    return [
        'Fonte: impressão em PDF do texto compilado do Planalto (3 páginas), enviada por Leo. Cabeçalho institucional, a anotação lateral "Conversão da Medida Provisória nº 399, de 1993" (registrada no cabeçalho) e o rodapé "Este texto não substitui o publicado no DOU de 29.1.1994" não transcritos no corpo.',
        '',
        '- Texto compilado sem trechos tachados: o Planalto publica só "Arts. 1º a 22 (Revogados pela Lei nº 9.393, de 19.12.96)" e "Art. 25. (Revogado ...)". Cada artigo revogado recebeu ID próprio (`art1` a `art22`, `art25`) com `#revogado`, para que remissões de outras normas tenham destino.',
        '- O PDF não traz assinaturas, só o fecho.',
        '- Anexo I (tipo 3, conteúdo normativo): três tabelas de 12 linhas cada, lidas do `pdftotext -layout` e conferidas contra a imagem das páginas 2 e 3. Cabeçalho de dois níveis achatado em "UTILIZAÇÃO EFETIVA DA ÁREA APROVEITÁVEL % — >80" etc.; na Tabela II o rótulo "HECTARES" fica numa linha própria no original. Valores transcritos como publicados, inclusive o ponto decimal em "0.07" (4ª linha das três tabelas), em vez de vírgula.',
        '- Título da Tabela III em duas linhas no original ("...DO PANTANAL MATOGROSSENSE / E SUL MATOGROSSENSE"); unido.',
        '- Norma fora do escopo ambiental, incluída por ser citada por normas ambientais (a Lei nº 4.771/1965 traz "(Vide Lei nº 8.847 de 1994)" no cabeçalho). Tags reduzidas ao mínimo.',
    ]

cfg = {
    'json': 'l8847', 'arquivo': 'lei-federal-8847-1994',
    'titulo': 'Lei Federal nº 8.847, de 28 de janeiro de 1994',
    'preambulo_re': r'^O PRESIDENTE',
    'niveis': {},
    'ementa_md': 'Dispõe sobre o Imposto sobre a Propriedade Territorial Rural (ITR) e dá outras providências.',
    'cabecalho': 'Anotação do Planalto no cabeçalho: "Conversão da [[medida-provisoria-399-1993|Medida Provisória nº 399, de 1993]]".',
    'fm': {
        'norma': 'Lei Federal nº 8.847/1994', 'arquivo': 'lei-federal-8847-1994', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '8847', 'ano': '1994', 'data_assinatura': '1994-01-28', 'data_publicacao': '1994-01-29',
        'publicacao': 'Diário Oficial da União de 29/01/1994', 'vigencia': 'na data da publicação (art. 26)',
        'orgao': 'Presidência da República',
        'ementa': '"Dispõe sobre o Imposto sobre a Propriedade Territorial Rural (ITR) e dá outras providências."',
        'situacao': 'vigente', 'texto': 'compilado (arts. 1º a 22 e 25 revogados pela Lei nº 9.393/1996)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF, 3 páginas; \\"Este texto não substitui o publicado no DOU de 29.1.1994\\", enviado por Leo"',
    },
    'cita_extra': ['medida-provisoria-399-1993'],
    'tags': {},
    'apos_assinatura': anexo,
    'relacao': [
        '- Fora do escopo ambiental da base. Lei do ITR que sucedeu a MP nº 399/1993; a [[lei-federal-4771-1965|Lei nº 4.771/1965]] (antigo Código Florestal) remete a ela no cabeçalho ("Vide Lei nº 8.847 de 1994").',
        '- Os arts. 1º a 22 e 25 (cálculo e cobrança do ITR) foram revogados pela [[lei-federal-9393-1996|Lei nº 9.393, de 19/12/1996]], que hoje rege o ITR (inclusive a exclusão das áreas de preservação permanente e de reserva legal da área tributável). Continuam no texto os arts. 23 e 24 (Taxa de Serviços Cadastrais do Incra e receitas da CNA, Contag e Senar) e o art. 26.',
        '- O Anexo I (alíquotas do ITR por tamanho do imóvel e grau de utilização) servia aos artigos revogados. O Planalto ainda o publica, sem anotação de revogação; a [[lei-federal-9393-1996|Lei nº 9.393/1996]] tem tabela de alíquotas própria (informação do conversor, não está no PDF). Na dúvida, tratar o Anexo I como sem aplicação e conferir na Lei nº 9.393/1996.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
