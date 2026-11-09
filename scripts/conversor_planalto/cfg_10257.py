from make import *
import tagger

REGRAS = [
    (r'plano diretor', '#plano-diretor'),
    (r'impacto de vizinhanca|\beiv\b', '#eiv'),
    (r'estudo previo de impacto ambiental|eia', '#eia-rima'),
    (r'politica urbana', '#politica-urbana'),
    (r'parcelamento|edificacao ou utilizacao compulsorios', '#parcelamento-solo'),
    (r'usucapiao', '#usucapiao'),
    (r'outorga onerosa', '#outorga-onerosa'),
    (r'operac\w+ urbanas? consorciad', '#operacao-urbana-consorciada'),
    (r'direito de preempcao', '#direito-preempcao'),
    (r'transferencia do direito de construir', '#transferencia-direito-construir'),
    (r'regularizacao fundiaria', '#regularizacao-fundiaria'),
    (r'riscos? de desastres|deslizamentos|inundac', '#area-risco'),
    (r'expansao urbana', '#expansao-urbana'),
    (r'gestao democratica|audiencias? publicas?|debates', '#participacao-publica'),
    (r'improbidade', '#improbidade-administrativa'),
    (r'patrimonio (cultural|historico)|paisagem', '#patrimonio-cultural'),
    (r'saneamento', '#saneamento'),
    (r'mobilidade|transporte', '#mobilidade-urbana'),
]

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ', 'texto de dispositivo revogado'))]
    rem = getattr(pr, 'revogados_com_texto', [])
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (23 páginas, a última só com o rodapé), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 11.7.2001 e retificado em 17.7.2001" não transcritos.',
        '',
        f'- Texto compilado: o PDF traz, tachadas, redações anteriores e dispositivos incluídos por medidas provisórias que perderam a eficácia ({len(drop)} trechos). Identificados pelos traços horizontais (PyMuPDF) e omitidos, conforme a regra de 06/10/2026 (só o texto em vigor). Entre eles: alíneas "t" e "u" do art. 4º, V, e o art. 42-A na redação da Medida Provisória nº 547/2011; o art. 53 (alteração da Lei nº 7.347/1985), mantido só com o rótulo e a anotação de revogação.',
        '- Anotações "Vigência" e "(Vigência)" ao lado de dispositivos (links do portal para a regra de vigência da lei alteradora) mantidas como anotação.',
        '- Ordinais com "o" sobrescrito transcritos como "º"; grafias anteriores ao Acordo Ortográfico ("cinqüenta", "freqüência", "conseqüente") mantidas.',
        '- Art. 4º, inciso V: as alíneas passam de "j" para "l", sem alínea "k", no original; mantido.',
        '- Art. 53 (acréscimo do inciso III ao art. 1º da Lei nº 7.347/1985): revogado pela Medida Provisória nº 2.180-35/2001; no PDF, o rótulo, a citação da Lei nº 7.347 e o bloco citado estão tachados, mas o traço não pegou "art. 1o" nem a citação da lei. Tratado como revogado (rótulo e anotação).',
        '- Art. 57-A na redação da Medida Provisória nº 1.065/2021 ("Vigência encerrada"): tachado no PDF e omitido; fica a redação da Lei nº 14.273/2021.',
        '- Dispositivos vetados mantidos com o rótulo e "(VETADO)", como no original.',
    ]
    if rem:
        out.append('- Dispositivos publicados com texto e anotação de revogação: texto retirado (regra de 06/10/2026): ' + ', '.join(f'`{i}`' for i, _ in rem) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

def patch(P):
    out = []
    bloco53 = False
    for r in P:
        t = r['t']
        if t.startswith('Art. 53. O art. 1o da Lei nº 7.347'):
            r = riscar(r, manter_anotacao=True); bloco53 = True
        elif bloco53:
            r = riscar(r)
            if '(NR)' in t: bloco53 = False
        elif r['s'] > 0.9 and t.endswith('Vigência encerrada'):
            r = riscar(r)
        out.append(r)
    return out

cfg = {
    'patch': patch,
    'json': 'l10257', 'arquivo': 'lei-federal-10257-2001',
    'titulo': 'Lei Federal nº 10.257, de 10 de julho de 2001',
    'preambulo_re': r'^O PRESIDENTE',
    'niveis': {'CAPITULO': 2, 'SECAO': 3},
    'revogado_remove_texto': True,
    'ementa_md': 'Regulamenta os arts. 182 e 183 da Constituição Federal, estabelece diretrizes gerais da política urbana e dá outras providências.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Mensagem de Veto nº 730", "Vigência" e "(Vide Lei nº 15.432, de 2026)".',
    'fm': {
        'norma': 'Lei Federal nº 10.257/2001', 'arquivo': 'lei-federal-10257-2001', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '10257', 'ano': '2001', 'data_assinatura': '2001-07-10', 'data_publicacao': '2001-07-11',
        'publicacao': 'Diário Oficial da União de 11/07/2001 (retificado em 17/07/2001)', 'vigencia': 'noventa dias após a publicação (art. 58)',
        'orgao': 'Presidência da República',
        'ementa': '"Regulamenta os arts. 182 e 183 da Constituição Federal, estabelece diretrizes gerais da política urbana e dá outras providências."',
        'apelido': 'Estatuto da Cidade',
        'situacao': 'vigente', 'texto': 'compilado (última alteração anotada: Lei nº 15.333/2026)',
        'regulamenta': '["[[constituicao-federal-1988]]"]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF (Safari/iOS), 23 páginas; \\"Este texto não substitui o publicado no DOU de 11.7.2001 e retificado em 17.7.2001\\", enviado por Leo"',
    },
    'cita_extra': ['constituicao-federal-1988'],
    'manual': [('os arts. 182 e 183 da Constituição Federal', 'os [[constituicao-federal-1988#art182|arts. 182]] e [[constituicao-federal-1988#art183|183 da Constituição Federal]]')],
    'tags': tagger.por_regras(REGRAS),
    'relacao': [
        '- Regulamenta os [[constituicao-federal-1988#art182|arts. 182]] e [[constituicao-federal-1988#art183|183 da Constituição Federal]] (política urbana).',
        '- O Estudo de Impacto de Vizinhança (arts. 36 a 38) não substitui o EIA/RIMA exigido nos termos da legislação ambiental (art. 38). No licenciamento, ver a [[resolucao-conama-237-1997|Resolução CONAMA nº 237/1997]] (art. 10, § 1º: certidão municipal de conformidade com o uso e ocupação do solo).',
        '- A [[lei-federal-11977-2009|Lei nº 11.977/2009]] alterou esta Lei (anotada no PDF).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
