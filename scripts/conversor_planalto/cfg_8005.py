from make import *
import tagger

REGRAS = [
    (r'divida ativa', '#divida-ativa'),
    (r'penalidade|multa', '#multa'),
    (r'auto de infracao', '#auto-infracao'),
    (r'ibama', '#ibama'),
    (r'parcela', '#parcelamento'),
    (r'taxas? de licenciamento', '#taxa-licenciamento'),
]

def notas(rd, pr, drop):
    return [
        'Fonte: impressão em PDF do texto do Planalto (2 páginas e uma página só com o rodapé), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, rodapé de cada página (endereço do portal, data e hora da impressão, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 23.3.1990" não transcritos.',
        '',
        '- O Planalto não anota alterações nesta Lei; não há trechos tachados no PDF.',
        '- Art. 10: publicado sem o ordinal e sem ponto depois do número ("Art. 10 Revogam-se"); mantido.',
        '- Art. 10 ("Revogam-se as disposições em contrário"): cláusula de revogação genérica (revogação tácita), sem norma indicada.',
        '- Ordinais com "o" sobrescrito transcritos como "º".',
    ]

cfg = {
    'json': 'l8005', 'arquivo': 'lei-federal-8005-1990',
    'titulo': 'Lei Federal nº 8.005, de 22 de março de 1990',
    'preambulo_re': r'^Faço saber',
    'fecho_re': r'^Senado Federal,',
    'niveis': {},
    'ementa_md': 'Dispõe sobre a cobrança e a atualização dos créditos do Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis (Ibama), e dá outras providências.',
    'cabecalho': 'Anotação do Planalto no cabeçalho: "Conversão da Medida Provisória nº 136, de 1990".',
    'fm': {
        'norma': 'Lei Federal nº 8.005/1990', 'arquivo': 'lei-federal-8005-1990', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '8005', 'ano': '1990', 'data_assinatura': '1990-03-22', 'data_publicacao': '1990-03-23',
        'publicacao': 'Diário Oficial da União de 23/03/1990', 'vigencia': 'na data da publicação (art. 9º)',
        'orgao': 'Congresso Nacional (promulgada pelo Presidente do Senado Federal)',
        'ementa': '"Dispõe sobre a cobrança e a atualização dos créditos do Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis (Ibama), e dá outras providências."',
        'situacao': 'vigente', 'texto': 'original (o Planalto não anota alterações)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF (Safari/iOS), 3 páginas; \\"Este texto não substitui o publicado no DOU de 23.3.1990\\", enviado por Leo"',
    },
    'cita_extra': ['medida-provisoria-136-1990'],
    'tags': tagger.por_regras(REGRAS),
    'relacao': [
        '- O [[decreto-federal-6514-2008|Decreto nº 6.514/2008]] regulamenta, entre outras, esta Lei no processo administrativo federal de apuração de infrações ambientais (preâmbulo); o desconto de 30% dos arts. 3º, § 2º, e 4º desta Lei é tratado no art. 113 daquele Decreto.',
        '- Os valores em BTN (art. 2º) e a correção pelo BTN Fiscal (art. 3º, § 1º) refletem índices extintos em 1991; a atualização dos créditos segue a legislação posterior (informação do conversor, não está no PDF).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
