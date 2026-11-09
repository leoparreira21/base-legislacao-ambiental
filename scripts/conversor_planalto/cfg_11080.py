from make import *
import tagger

# Decreto alterador cujas alterações foram, em boa parte, revogadas pelo Decreto nº 11.373/2023. No PDF, o texto revogado
# está tachado e a anotação "(Revogado pelo Decreto nº 11.373, de 2023)" fica sem tachado, às vezes com vários
# dispositivos citados no mesmo parágrafo. O patch separa os dispositivos e deixa, de cada trecho tachado, só o rótulo,
# o fecho da citação (” (NR)) e a anotação.

RE_INI = re.compile(r'^[“"]?(Art\.|§|Parágrafo$|[IVXLC]+$|[a-z]\)$|[…\.]{5,})')
RE_ROT = re.compile(r'^[“"]?(Art\.\s*\d+[º°o]?(?:-[A-Z])?\.?|§\s*\d+[º°o]?|Parágrafo único\.|[IVXLC]+\s*-|[a-z]\))')
PONT = re.compile(r'^[…\.]+[”"]?$')

def _segs(toks):
    segs = [[]]
    for k, t in enumerate(toks):
        w = t.lstrip('~')
        if segs[-1] and RE_INI.match(w):
            prev = toks[k - 1].lstrip('~')
            nxt = toks[k + 1].lstrip('~') if k + 1 < len(toks) else ''
            ok = (re.search(r'[.;:)”"]$', prev) or PONT.match(prev)) and (not re.fullmatch(r'[IVXLC]+', w) or nxt in ('-', '–'))
            if ok:
                segs.append([])
        segs[-1].append(t)
    return segs

def patch(P):
    out = []
    for r in P:
        if r['s'] == 0:
            out.append(r); continue
        for seg in _segs(r['st'].split(' ')):
            words = [t.lstrip('~') for t in seg]
            struck = [t for t in seg if t.startswith('~')]
            keep = [t for t in seg if not t.startswith('~')]
            txt = ' '.join(words)
            r2 = dict(r)
            if not struck:
                r2['t'] = r2['st'] = txt; r2['s'] = 0; out.append(r2); continue
            if all(PONT.match(w) for w in words):
                continue   # linha pontilhada tachada
            rot = RE_ROT.match(re.sub(r'\s+', ' ', ' '.join(t.lstrip('~') for t in struck)))
            sw = [t.lstrip('~') for t in struck]
            fecho = '” (NR)' if sw and (sw[-1].endswith('”') or (sw[-1] == '(NR)' and len(sw) > 1 and sw[-2].endswith('”'))) else ''
            ann = ' '.join(t for t in keep if not PONT.match(t))
            ann = re.sub(r'^(ou|e)\s+', '', ann)   # resto não tachado ("ou") antes da anotação
            partes = [p for p in ((rot.group(0).rstrip() if rot else ''), fecho, ann) if p]
            if not partes:
                continue
            r2['t'] = r2['st'] = ' '.join(partes); r2['s'] = 0
            out.append(r2)
    return out

REGRAS = [
    (r'conciliacao', '#conciliacao-ambiental'),
    (r'multa', '#multa'),
    (r'auto de infracao', '#auto-infracao'),
    (r'reincid', '#reincidencia'),
    (r'conversao', '#conversao-multa'),
    (r'recurso', '#recurso-administrativo'),
]

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ',))]
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (15 páginas, a última só com o rodapé), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 24.5.2022 - Edição extra" não transcritos.',
        '',
        '- Grande parte das alterações deste Decreto ao [[decreto-federal-6514-2008|Decreto nº 6.514/2008]] (conciliação ambiental e adesão às soluções legais: arts. 95-A, 95-B, 96, §§ 4º e 5º, 97-A, 97-B, 98-A, 98-B, 98-D, 99, 113, 116, 119, 122, 142, 143, 146, 148 e outros) foi revogada pelo [[decreto-federal-11373-2023|Decreto nº 11.373/2023]]. No PDF, o texto revogado está tachado e a anotação de revogação não. Pela regra de 06/10/2026 (só o texto em vigor), ficaram, de cada dispositivo citado revogado, o rótulo, o fecho da citação ("” (NR)") e a anotação; o texto foi omitido. A redação hoje em vigor está no próprio [[decreto-federal-6514-2008|Decreto nº 6.514/2008]].',
        '- Linhas pontilhadas tachadas omitidas; as não tachadas mantidas como no original.',
        '- No PDF, vários dispositivos citados aparecem num só parágrafo (ex.: o fim da citação do art. 122 e o inciso III; as citações dos arts. 142 a 148); foram separados por dispositivo.',
        '- Art. 1º, citação do art. 122: o "ou" do fim do inciso II ficou sem tachado no PDF; descartado com o texto revogado.',
        '- Art. 2º, IV, "e": os itens 3 e 4 saem na mesma linha no PDF ("... do § 1º; e 4. os § 2º e § 3º;"); separados.',
        '- O art. 2º revoga dispositivos do Decreto nº 6.514/2008 e partes do art. 1º dos Decretos nº 6.686/2008, 9.179/2017 e 9.760/2019, além do Decreto nº 10.198/2020 por inteiro.',
    ]
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'd11080', 'arquivo': 'decreto-federal-11080-2022',
    'titulo': 'Decreto Federal nº 11.080, de 24 de maio de 2022',
    'preambulo_re': r'^O PRESIDENTE', 'preambulo_n': 2,
    'patch': patch,
    'split': lambda t: re.split(r'(?<=; e) (?=4\. os § 2º)', t),
    'niveis': {},
    'ementa_md': 'Altera o Decreto nº 6.514, de 22 de julho de 2008, para dispor sobre as infrações e sanções administrativas por condutas e atividades lesivas ao meio ambiente.',
    'fm': {
        'norma': 'Decreto Federal nº 11.080/2022', 'arquivo': 'decreto-federal-11080-2022', 'tipo': 'decreto', 'esfera': 'federal',
        'numero': '11080', 'ano': '2022', 'data_assinatura': '2022-05-24', 'data_publicacao': '2022-05-24',
        'publicacao': 'Diário Oficial da União de 24/05/2022 (edição extra)', 'vigencia': 'na data da publicação (art. 3º)',
        'orgao': 'Presidência da República',
        'ementa': '"Altera o Decreto nº 6.514, de 22 de julho de 2008, para dispor sobre as infrações e sanções administrativas por condutas e atividades lesivas ao meio ambiente."',
        'situacao': 'vigente', 'texto': 'compilado (alterações revogadas em parte pelo Decreto nº 11.373/2023)',
        'regulamenta': '[]', 'regulamentado_por': '[]',
        'altera': fm_list(['decreto-federal-6514-2008', 'decreto-federal-6686-2008', 'decreto-federal-9179-2017', 'decreto-federal-9760-2019']),
        'revoga': fm_list(['decreto-federal-10198-2020']),
        'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Secretaria-Geral), impressão do navegador em PDF (Safari/iOS), 15 páginas; \\"Este texto não substitui o publicado no DOU de 24.5.2022 - Edição extra\\", enviado por Leo"',
    },
    'alterado_por_extra': ['decreto-federal-11373-2023'],
    'tags': tagger.por_regras(REGRAS),
    'relacao': [
        '- Norma alteradora do [[decreto-federal-6514-2008|Decreto nº 6.514/2008]]. As novas redações já estão incorporadas ao texto compilado daquele Decreto; as que o [[decreto-federal-11373-2023|Decreto nº 11.373/2023]] revogou não estão mais lá.',
        '- O art. 149-A incluído no Decreto nº 6.514/2008 (reincidência só para autos lavrados a partir da vigência deste Decreto) continua em vigor.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
