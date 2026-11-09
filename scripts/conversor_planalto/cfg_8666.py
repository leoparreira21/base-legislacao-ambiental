from make import *
import tagger

# A Lei 8.666/1993 foi revogada por inteiro pela Lei 14.133/2021 e o Planalto publica todo o texto tachado
# (redações anteriores e última redação, sem distinção). O patch tira o tachado de tudo, e o parser fica com a
# última entrada de cada número (dup_ultima): é o texto compilado até a revogação.

def _so_mp_caduca(t):
    """True se as anotações de redação/inclusão do trecho citam só medidas provisórias comuns (sem reedição
    "-NN" de 2001, que continuam em vigor pela EC 32/2001): redação de MP que perdeu a eficácia ou foi
    substituída pela lei de conversão."""
    _, anns = split_annot(t)
    refs = [(k, sl) for a in anns for k, sl, _ in kinds_of(a) if k in ('alt', 'inc')]
    return bool(refs) and all(re.fullmatch(r'medida-provisoria-\d+-\d{4}', sl) for _, sl in refs)

def patch(P):
    out = []
    for r in P:
        for toks in segmentos(r['t'].split(' ')):
            t = ' '.join(toks)
            r2 = dict(r); r2['t'] = r2['st'] = t; r2['s'] = 0
            if _so_mp_caduca(t):
                MP_DESCARTADOS.append(t[:90]); continue
            out.append(r2)
    return out

MP_DESCARTADOS = []

REGRAS = [
    (r'licenca ambiental|licenciamento ambiental|impacto ambiental|ambiental', '#sustentabilidade'),
    (r'dispensavel|dispensada|inexigivel|inexigibilidade', '#dispensa-licitacao'),
    (r'licitac', '#licitacao'),
    (r'contrato', '#contrato-administrativo'),
    (r'projeto basico|projeto executivo', '#projeto-engenharia'),
    (r'obras? e servicos de engenharia|obras e servicos', '#obra-engenharia'),
    (r'garantia', '#garantia-contratual'),
    (r'sanc|multa|suspensao temporaria|declaracao de inidoneidade', '#sancao'),
    (r'pena - |detencao', '#crime'),
    (r'recurso\b|representacao|pedido de reconsideracao', '#recurso-administrativo'),
    (r'\bprazo', '#prazo'),
]

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ', 'texto de dispositivo revogado'))]
    rem = getattr(pr, 'revogados_com_texto', [])
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto ("l8666cons", 68 páginas), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, as anotações laterais do cabeçalho (registradas acima), "Texto para impressão", rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 22.6.1993, republicado em 6.7.1994 e retificado em 6.7.1994" não transcritos.',
        '',
        '- Lei revogada por inteiro pela [[lei-federal-14133-2021|Lei nº 14.133/2021]] (arts. 89 a 108 na data da publicação daquela Lei; o restante em 30/12/2023, art. 193 da Lei nº 14.133/2021). Transcrita porque normas da base ainda remetem a ela e porque rege os contratos assinados antes da revogação (art. 190 da Lei nº 14.133/2021).',
        f'- Texto todo tachado no PDF: o Planalto tacha a lei inteira por estar revogada, e as redações anteriores ficam tachadas do mesmo jeito que a última. Não há como separá-las pelo tachado. O conversor ficou, para cada número de dispositivo, com a última entrada do PDF (a ordem do Planalto é original → redações seguintes), que é a redação vigente na data da revogação. Foram descartadas {getattr(pr, "substituidos", 0)} entradas anteriores de mesmo número. As redações anteriores continuam no PDF do Planalto.',
        f'- Entradas cuja única anotação de redação ou inclusão é de medida provisória comum (não reeditada em 2001) foram descartadas antes dessa escolha ({len(set(MP_DESCARTADOS))}): são redações de MP que perderam a eficácia ou foram substituídas pela lei de conversão (ex.: art. 3º, § 2º, incisos I a III, na redação da Medida Provisória nº 495/2010, que a Lei nº 12.349/2010 não manteve). Medidas provisórias reeditadas até 2001 ("nº 2.xxx-NN") continuam em vigor (EC nº 32/2001) e não foram descartadas.',
        '- Dispositivos revogados antes da revogação total (anotação "(Revogado pela ...)"): mantidos só o rótulo, o ID e a anotação, pela regra de 06/10/2026.',
        '- Ordinais com "o" sobrescrito transcritos como "º"; grafias anteriores ao Acordo Ortográfico ("subseqüentes", "freqüência") mantidas.',
        '- Dispositivos vetados mantidos com o rótulo e "(VETADO)", como no original.',
    ]
    if rem:
        out.append(f'- Dispositivos publicados com texto e anotação de revogação: texto retirado ({len(rem)}): ' + ', '.join(f'`{i}`' for i, _ in rem) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'l8666', 'arquivo': 'lei-federal-8666-1993',
    'titulo': 'Lei Federal nº 8.666, de 21 de junho de 1993',
    'preambulo_re': r'^O PRESIDENTE',
    'patch': patch, 'dup_ultima': True,
    'niveis': {'CAPITULO': 2, 'SECAO': 3},
    'revogado_remove_texto': True,
    'ementa_md': 'Regulamenta o art. 37, inciso XXI, da Constituição Federal, institui normas para licitações e contratos da Administração Pública e dá outras providências.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Mensagem de veto", "(Vide Decreto nº 99.658, de 1990)", "(Vide Decreto nº 1.054, de 1994)", "(Vide Decreto nº 7.174, de 2010)", "(Vide Medida Provisória nº 544, de 2011)", "(Vide Lei nº 12.598, de 2012)", "(Vide Lei nº 13.800, de 2019)", "(Revogado pela Lei nº 14.133, de 2021)" e "Vigência" (duas vezes).',
    'fm': {
        'norma': 'Lei Federal nº 8.666/1993', 'arquivo': 'lei-federal-8666-1993', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '8666', 'ano': '1993', 'data_assinatura': '1993-06-21', 'data_publicacao': '1993-06-22',
        'publicacao': 'Diário Oficial da União de 22/06/1993 (republicado e retificado em 06/07/1994)',
        'vigencia': 'na data da publicação (art. 125); revogada pela Lei nº 14.133/2021 (arts. 89 a 108 em 01/04/2021; o restante em 30/12/2023)',
        'orgao': 'Presidência da República',
        'ementa': '"Regulamenta o art. 37, inciso XXI, da Constituição Federal, institui normas para licitações e contratos da Administração Pública e dá outras providências."',
        'apelido': 'Lei de Licitações de 1993 (revogada)',
        'situacao': 'revogada', 'texto': 'compilado até a revogação',
        'regulamenta': '["[[constituicao-federal-1988]]"]', 'regulamentado_por': '[]',
        'altera': '[]', 'revoga': '[]', 'revogado_por': '["[[lei-federal-14133-2021]]"]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), texto compilado l8666cons, impressão do navegador em PDF (Safari/iOS), 68 páginas; \\"Este texto não substitui o publicado no DOU de 22.6.1993, republicado em 6.7.1994 e retificado em 6.7.1994\\", enviado por Leo"',
    },
    'cita_extra': ['constituicao-federal-1988'],
    'manual': [('Regulamenta o art. 37, inciso XXI, da Constituição Federal', 'Regulamenta o [[constituicao-federal-1988#art37_cpt_inc21|art. 37, inciso XXI, da Constituição Federal]]')],
    'tags': tagger.por_regras(REGRAS),
    'relacao': [
        '- Revogada pela [[lei-federal-14133-2021|Lei nº 14.133/2021]] ([[lei-federal-14133-2021#art193|art. 193]]). Os contratos assinados antes continuam regidos por ela ([[lei-federal-14133-2021#art190|art. 190]]), e as remissões de outras leis a esta passam a valer para a Lei nº 14.133/2021 ([[lei-federal-14133-2021#art189|art. 189]]).',
        '- Normas da base que ainda remetem a esta Lei (arts. 23, 24, 26 e 112): ao aplicá-las a contratações novas, usar os dispositivos correspondentes da Lei nº 14.133/2021.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
