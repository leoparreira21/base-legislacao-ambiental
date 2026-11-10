from make import *
import tagger

REGRAS = [
    (r'multa diaria|multa-dia', '#multa-diaria'),
    (r'\bmulta\b', '#multa'),
    (r'auto de infracao', '#auto-infracao'),
    (r'\bembarg', '#embargo'),
    (r'apreens', '#apreensao'),
    (r'demolic', '#demolicao'),
    (r'advertencia', '#advertencia'),
    (r'conversao (da|de) multa|servicos de preservacao, melhoria e recuperacao', '#conversao-multa'),
    (r'conciliacao', '#conciliacao-ambiental'),
    (r'prescri', '#prescricao'),
    (r'reincid|cometimento de nova infracao', '#reincidencia'),
    (r'\bfauna\b|espec\w+ da fauna|animais', '#fauna'),
    (r'\bflora\b|vegetacao|florest', '#flora'),
    (r'reserva legal', '#reserva-legal'),
    (r'preservacao permanente', '#app'),
    (r'unidades? de conservacao', '#unidade-conservacao'),
    (r'\bpesca', '#pesca'),
    (r'poluic|lancamento de residuos|emissao', '#poluicao'),
    (r'licenca|autorizacao ambiental|sem licenca|licenciamento', '#licenciamento-ambiental'),
    (r'residuos', '#residuo-solido'),
    (r'agrotox', '#agrotoxico'),
    (r'patrimonio genetico|conhecimento tradicional', '#patrimonio-genetico'),
    (r'recurso\b|recursos administrativos', '#recurso-administrativo'),
    (r'defesa|alegacoes finais', '#defesa-administrativa'),
    (r'termo de compromisso', '#termo-compromisso'),
    (r'ordenamento urbano|patrimonio cultural', '#patrimonio-cultural'),
]

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ', 'texto de dispositivo revogado', 'ID duplicado', 'revogado de redação anterior'))
           and not re.match(r'sem marcador \(unido a [\w-]+\): (Multa|Penalidade)', l) and '-dup' not in l]
    rem = getattr(pr, 'revogados_com_texto', [])
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (63 páginas), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, a anotação lateral "Texto compilado", rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 23.7.2008" não transcritos.',
        '',
        f'- Texto compilado: o PDF traz, tachadas, as redações anteriores e os dispositivos incluídos e depois revogados ({len(drop)} trechos). Identificados pelos traços horizontais (PyMuPDF) e omitidos, conforme a regra de 06/10/2026 (só o texto em vigor). O texto omitido pode reger autos lavrados antes da mudança; nesses casos, consultar o compilado do Planalto.',
        '- Os blocos "Multa de R$ ..." que se seguem ao caput dos tipos infracionais (Capítulo I, Seção III) não têm rótulo próprio no original; ficam unidos ao dispositivo anterior, como no Planalto.',
        '- Art. 152: a anotação "(Redação dada pelo Decreto nº 7.719, de 2012))" fecha com dois parênteses no original; o parêntese a mais foi retirado para reconhecer a anotação.',
        '- Entradas revogadas que pertenciam a redações anteriores já tachadas (incisos I e II do antigo § 1º do art. 20, revogados pelo Decreto nº 12.189/2024; parágrafo único do art. 140-B revogado pelo Decreto nº 9.179/2017, anterior ao atual, incluído pelo Decreto nº 11.373/2023): o PDF mostra o rótulo tachado e a anotação de revogação sem tachado; descartadas para não duplicar o número do dispositivo em vigor.',
        '- Art. 122, parágrafo único (redação do Decreto nº 11.080/2022, revogado com seus incisos pelo Decreto nº 11.373/2023): a anotação de revogação do inciso I caiu no começo da página seguinte; levada ao inciso I.',
        '- Ordinais com "o" sobrescrito transcritos como "º"; grafias anteriores ao Acordo Ortográfico ("cinqüenta", "conseqüência") mantidas.',
        '- Dispositivos vetados ou revogados mantidos com o rótulo e a anotação, sem o texto.',
    ]
    if rem:
        out.append('- Dispositivos publicados com texto e anotação de revogação: texto retirado (regra de 06/10/2026): ' + ', '.join(f'`{i}`' for i, _ in rem) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

def fix(t):
    return t.replace('de 2012))', 'de 2012)').replace('de 2011))', 'de 2011)')

def patch(P):
    # art. 122: a anotação de revogação do inciso I do antigo parágrafo único caiu no começo da página seguinte
    P = [dict(r) for r in P]
    for i, r in enumerate(P):
        rv = '(Revogado pelo Decreto nº 11.373, de 2023)'
        if r['st'].endswith('~I ~- ~por ~via ~postal ~com ~aviso ~de ~recebimento; ~(Incluído ~pelo ~Decreto ~nº ~11.080, ~de ~2022)') \
                and P[i + 1]['st'].startswith(rv + ' ~II'):
            r['st'] += ' ' + rv; r['t'] += ' ' + rv
            P[i + 1]['st'] = P[i + 1]['st'][len(rv) + 1:]; P[i + 1]['t'] = P[i + 1]['t'][len(rv) + 1:]
    return P

cfg = {
    'patch': patch,
    'fix': fix,
    'json': 'd6514', 'arquivo': 'decreto-federal-6514-2008',
    'titulo': 'Decreto Federal nº 6.514, de 22 de julho de 2008',
    'preambulo_re': r'^O PRESIDENTE', 'preambulo_n': 2,
    'niveis': {'CAPITULO': 2, 'SECAO': 3, 'SUBSECAO': 4},
    'revogado_remove_texto': True,
    'ementa_md': 'Dispõe sobre as infrações e sanções administrativas ao meio ambiente, estabelece o processo administrativo federal para apuração destas infrações, e dá outras providências.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Texto compilado" e "Vigência".',
    'fm': {
        'norma': 'Decreto Federal nº 6.514/2008', 'arquivo': 'decreto-federal-6514-2008', 'tipo': 'decreto', 'esfera': 'federal',
        'numero': '6514', 'ano': '2008', 'data_assinatura': '2008-07-22', 'data_publicacao': '2008-07-23',
        'publicacao': 'Diário Oficial da União de 23/07/2008', 'vigencia': 'na data da publicação (art. 154)',
        'orgao': 'Presidência da República',
        'ementa': '"Dispõe sobre as infrações e sanções administrativas ao meio ambiente, estabelece o processo administrativo federal para apuração destas infrações, e dá outras providências."',
        'apelido': 'Decreto de infrações e sanções ambientais',
        'situacao': 'vigente', 'texto': 'compilado',
        'regulamenta': '["[[lei-federal-9605-1998]]"]', 'regulamentado_por': '[]',
        'altera': fm_list(['decreto-federal-5975-2006', 'decreto-federal-6321-2007']),
        'revoga': fm_list(['decreto-federal-3179-1999', 'decreto-federal-3919-2001', 'decreto-federal-4592-2003', 'decreto-federal-5523-2005']),
        'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF (Safari/iOS), 63 páginas; \\"Este texto não substitui o publicado no DOU de 23.7.2008\\", enviado por Leo"',
    },
    'manual': [
        ('nas Leis nos 9.784, de 29 de janeiro de 1999, 8.005, de 22 de março de 1990, 9.873, de 23 de novembro de 1999, e 6.938, de 31 de agosto de 1981',
         'nas Leis nos [[lei-federal-9784-1999|9.784, de 29 de janeiro de 1999]], [[lei-federal-8005-1990|8.005, de 22 de março de 1990]], [[lei-federal-9873-1999|9.873, de 23 de novembro de 1999]], e [[lei-federal-6938-1981|6.938, de 31 de agosto de 1981]]'),
        ('Ficam revogados os Decretos nos 3.179, de 21 de setembro de 1999, 3.919, de 14 de setembro de 2001, 4.592, de 11 de fevereiro de 2003, 5.523, de 25 de agosto de 2005, os arts. 26 e 27 do Decreto nº 5.975, de 30 de novembro de 2006, e os arts. 12 e 13 do Decreto nº 6.321, de 21 de dezembro de 2007.',
         'Ficam revogados os Decretos nos [[decreto-federal-3179-1999|3.179, de 21 de setembro de 1999]], [[decreto-federal-3919-2001|3.919, de 14 de setembro de 2001]], [[decreto-federal-4592-2003|4.592, de 11 de fevereiro de 2003]], [[decreto-federal-5523-2005|5.523, de 25 de agosto de 2005]], os [[decreto-federal-5975-2006#art26|arts. 26]] e [[decreto-federal-5975-2006#art27|27 do Decreto nº 5.975, de 30 de novembro de 2006]], e os [[decreto-federal-6321-2007#art12|arts. 12]] e [[decreto-federal-6321-2007#art13|13 do Decreto nº 6.321, de 21 de dezembro de 2007]].'),
    ],
    'cita_extra': ['decreto-federal-3179-1999', 'decreto-federal-3919-2001', 'decreto-federal-4592-2003', 'decreto-federal-5523-2005', 'decreto-federal-5975-2006', 'decreto-federal-6321-2007', 'lei-federal-9784-1999', 'lei-federal-8005-1990', 'lei-federal-9873-1999', 'lei-federal-6938-1981'],
    'tags': tagger.por_regras(REGRAS, max_tags=6),
    'relacao': [
        '- Regulamenta o Capítulo VI (infração administrativa) da [[lei-federal-9605-1998|Lei nº 9.605/1998]] e, no processo administrativo federal, aplica as Leis nº [[lei-federal-9784-1999|9.784/1999]], [[lei-federal-8005-1990|8.005/1990]], [[lei-federal-9873-1999|9.873/1999]] e [[lei-federal-6938-1981|6.938/1981]] (preâmbulo).',
        '- Art. 153: revoga por inteiro os Decretos nº [[decreto-federal-3179-1999|3.179/1999]] (regulamento anterior da Lei nº 9.605/1998), [[decreto-federal-3919-2001|3.919/2001]], [[decreto-federal-4592-2003|4.592/2003]] e [[decreto-federal-5523-2005|5.523/2005]], e em parte os Decretos nº [[decreto-federal-5975-2006|5.975/2006]] (arts. 26 e 27) e [[decreto-federal-6321-2007|6.321/2007]] (arts. 12 e 13). Nenhum deles está na base.',
        '- A redação atual dos dispositivos do processo administrativo (conciliação, defesa, alegações finais, intimação) resulta das alterações dos Decretos nº [[decreto-federal-9760-2019|9.760/2019]], [[decreto-federal-11080-2022|11.080/2022]] e [[decreto-federal-11373-2023|11.373/2023]]; este último revogou boa parte das mudanças de 2022 e restabeleceu redações anteriores.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
