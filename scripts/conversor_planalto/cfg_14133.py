from make import *
import tagger

REGRAS = [
    (r'licenciamento ambiental|licenca previa|licencas? ambienta', '#licenciamento-ambiental'),
    (r'impacto ambiental|ambientalmente|sustentabilidade|meio ambiente|residuos solidos', '#sustentabilidade'),
    (r'dispensa de licitacao|dispensavel|inexigib', '#dispensa-licitacao'),
    (r'licitac', '#licitacao'),
    (r'contrato', '#contrato-administrativo'),
    (r'estudo tecnico preliminar', '#estudo-tecnico-preliminar'),
    (r'termo de referencia', '#termo-referencia'),
    (r'projeto basico|projeto executivo|anteprojeto', '#projeto-engenharia'),
    (r'obras? e servicos? de engenharia|obra de engenharia', '#obra-engenharia'),
    (r'desapropria', '#desapropriacao'),
    (r'portal nacional de contratacoes publicas|pncp', '#pncp'),
    (r'garantia', '#garantia-contratual'),
    (r'infrac|sanc|multa|impedimento de licitar|declaracao de inidoneidade', '#sancao'),
    (r'crime|pena -|reclusao', '#crime'),
    (r'recurso\b|pedido de reconsideracao', '#recurso-administrativo'),
    (r'credenciamento|pre-qualificacao|registro de precos|registro cadastral', '#procedimento-auxiliar'),
    (r'fiscal do contrato|fiscaliza', '#fiscalizacao'),
    (r'\bprazo', '#prazo'),
]

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ', 'texto de dispositivo revogado'))]
    rem = getattr(pr, 'revogados_com_texto', [])
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (101 páginas, a última só com o rodapé), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 1º.4.2021 - Edição extra-F" não transcritos.',
        '',
        f'- Texto compilado: o PDF traz, tachados, os rótulos "(VETADO)" dos dispositivos cujo veto foi derrubado, redações anteriores e anotações "(Vide Decreto nº ...)" de decretos de atualização de valores já substituídos ({len(drop)} trechos e partes de parágrafo). Identificados pelos traços horizontais (PyMuPDF) e omitidos, conforme a regra de 06/10/2026 (só o texto em vigor).',
        '- Partes vetadas promulgadas: o PDF traz, depois das assinaturas (págs. 98 a 100), o ato de promulgação de 10/06/2021 (Congresso Nacional, art. 66, § 5º, da Constituição) com o texto do art. 37, § 2º; art. 54, § 1º; art. 115, § 4º; e art. 175, § 2º. Esses dispositivos já estão no corpo, no lugar do "(VETADO)" tachado, com a anotação do Planalto; o ato não foi transcrito de novo. Conferido o texto de cada um com o corpo.',
        '- Valores em reais (limites de dispensa, grande vulto etc.): são os do texto da Lei; o Planalto anota "(Vide Decreto nº ...)" com os decretos anuais de atualização (art. 182). Os valores atualizados estão nesses decretos, não no texto.',
        '- Art. 178 (Capítulo II-B do Código Penal): o bloco citado foi reunido numa só citação; as rubricas dos tipos penais ("Contratação direta ilegal", "Frustração do caráter competitivo de licitação" etc.), que no original ficam em linha própria, ficaram unidas ao parágrafo anterior.',
        '- Ordinais com "o" sobrescrito transcritos como "º".',
        '- Dispositivos vetados mantidos com o rótulo e "(VETADO)", como no original.',
    ]
    if rem:
        out.append('- Dispositivos publicados com texto e anotação de revogação: texto retirado (regra de 06/10/2026): ' + ', '.join(f'`{i}`' for i, _ in rem) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'l14133', 'arquivo': 'lei-federal-14133-2021',
    'titulo': 'Lei Federal nº 14.133, de 1º de abril de 2021',
    'preambulo_re': r'^O PRESIDENTE DA REPÚBLICA Faço saber que o Congresso Nacional decreta e eu sanciono',
    'niveis': {'TITULO': 2, 'CAPITULO': 3, 'SECAO': 4, 'SUBSECAO': 5},
    'revogado_remove_texto': True,
    'ementa_md': 'Lei de Licitações e Contratos Administrativos.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Mensagem de veto", "Promulgação partes vetadas", "Regulamento" (duas vezes), "(Vide Decreto nº 12.174, de 2024)", "(Vide Decreto nº 12.343, de 2024)", "(Vide Decreto nº 12.807, de 2025)" e "Vigência" (duas vezes).',
    'fm': {
        'norma': 'Lei Federal nº 14.133/2021', 'arquivo': 'lei-federal-14133-2021', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '14133', 'ano': '2021', 'data_assinatura': '2021-04-01', 'data_publicacao': '2021-04-01',
        'publicacao': 'Diário Oficial da União de 01/04/2021 (edição extra-F); partes vetadas promulgadas em 10/06/2021', 'vigencia': 'na data da publicação (art. 194)',
        'orgao': 'Presidência da República',
        'ementa': '"Lei de Licitações e Contratos Administrativos."',
        'apelido': 'Nova Lei de Licitações',
        'situacao': 'vigente', 'texto': 'compilado',
        'regulamenta': '[]', 'regulamentado_por': '[]',
        'altera': fm_list(['decreto-lei-federal-2848-1940', 'lei-federal-13105-2015', 'lei-federal-8987-1995', 'lei-federal-11079-2004', 'lei-federal-12462-2011']),
        'revoga': fm_list(['lei-federal-8666-1993', 'lei-federal-10520-2002']),
        'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Secretaria-Geral), impressão do navegador em PDF (Safari/iOS), 101 páginas; \\"Este texto não substitui o publicado no DOU de 1º.4.2021 - Edição extra-F\\", enviado por Leo"',
    },
    'tags': tagger.por_regras(REGRAS),
    'relacao': [
        '- Substituiu a [[lei-federal-8666-1993|Lei nº 8.666/1993]], a [[lei-federal-10520-2002|Lei nº 10.520/2002]] (pregão) e os arts. 1º a 47-A da [[lei-federal-12462-2011|Lei nº 12.462/2011]] (RDC), revogados ao fim do prazo de transição do art. 193, II (30/12/2023, conforme o prazo dado pela Lei Complementar nº 198/2023; informação do conversor, não está no PDF). Contratos assinados sob a lei antiga continuam regidos por ela (art. 190).',
        '- Dispositivos que tratam de licenciamento ambiental ou de impacto ambiental (busca do conversor): [[#art6_cpt_inc24_alie|art. 6º, XXIV, "e"]], [[#art6_cpt_inc25|XXV]] (anteprojeto e projeto básico); [[#art18_par1_inc12|art. 18, § 1º, XII]] (estudo técnico preliminar); [[#art25_par5|art. 25, §§ 5º]] e [[#art25_par6|6º]] (responsabilidade pelo licenciamento no edital); [[#art34_par1|art. 34, § 1º]]; [[#art42_cpt_inc3|art. 42, III]]; [[#art45|art. 45]] (normas ambientais nas licitações de obras); [[#art75_cpt_inc4_alid|art. 75, IV, "d"]] e [[#art75_cpt_inc4_alij|"j"]]; [[#art115_par4|art. 115, § 4º]] (manifestação ou licença prévia antes do edital); [[#art124_par2|art. 124, § 2º]]; [[#art137_cpt_inc6|art. 137, VI]] e [[#art137_par2_inc5|§ 2º, V]]; [[#art144|art. 144]]; [[#art147_cpt_inc2|art. 147, II e III]]; [[#art184-a_par3|art. 184-A, § 3º]].',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
