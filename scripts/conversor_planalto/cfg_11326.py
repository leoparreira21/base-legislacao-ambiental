from make import *

def notas(rd, pr, drop):
    return [
        'Fonte: impressão em PDF do texto compilado do Planalto (3 páginas), enviada por Leo. Cabeçalho institucional, links laterais ("Regulamento", duas vezes) e o rodapé "Este texto não substitui o publicado no DOU de 25.7.2006" não transcritos.',
        '',
        f'- Texto compilado: o PDF traz, tachada, a redação original do art. 3º, inciso III ("tenha renda familiar predominantemente originada de atividades econômicas vinculadas ao próprio estabelecimento ou empreendimento;"). Identificada pelos traços horizontais (PyMuPDF) e omitida, conforme a regra de 06/10/2026 (só o texto em vigor).',
        '- Art. 3º, § 2º, inciso IV: termina em ponto final, seguido dos incisos V e VI incluídos pela Lei nº 12.512/2011; mantido como publicado.',
        '- Art. 5º, inciso XII: termina em ponto final, seguido dos incisos XIII e XIV incluídos pela Lei nº 14.828/2024; inciso XIII publicado sem espaço depois do travessão ("XIII -modernização"). Mantidos como publicados.',
        '- Art. 3º, § 2º, incisos V e VI: espaço antes do ponto e vírgula/ponto ("art. 3º ;", "art. 3º ."), e art. 7º ("publicação ."); mantidos.',
        '- Grafias anteriores ao Acordo Ortográfico ("mão-de-obra", "aqüicultores", "eqüidade", "infra-estrutura") mantidas.',
        '- Ordinais com "o" sobrescrito transcritos como "º".',
        '- Norma fora do escopo ambiental, incluída por ser citada por normas ambientais da base (definição de agricultor familiar, art. 3º). Tags reduzidas ao mínimo.',
    ]

cfg = {
    'json': 'l11326', 'arquivo': 'lei-federal-11326-2006',
    'titulo': 'Lei Federal nº 11.326, de 24 de julho de 2006',
    'preambulo_re': r'^O PRESIDENTE',
    'niveis': {},
    'ementa_md': 'Estabelece as diretrizes para a formulação da Política Nacional da Agricultura Familiar e Empreendimentos Familiares Rurais.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Regulamento" (duas vezes; links do portal, sem texto no PDF).',
    'fm': {
        'norma': 'Lei Federal nº 11.326/2006', 'arquivo': 'lei-federal-11326-2006', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '11326', 'ano': '2006', 'data_assinatura': '2006-07-24', 'data_publicacao': '2006-07-25',
        'publicacao': 'Diário Oficial da União de 25/07/2006', 'vigencia': 'na data da publicação (art. 7º)',
        'orgao': 'Presidência da República',
        'ementa': '"Estabelece as diretrizes para a formulação da Política Nacional da Agricultura Familiar e Empreendimentos Familiares Rurais."',
        'apelido': 'Lei da Agricultura Familiar',
        'situacao': 'vigente', 'texto': 'compilado (atualizado até a Lei nº 14.828/2024, a mais recente anotada no PDF)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF, 3 páginas; \\"Este texto não substitui o publicado no DOU de 25.7.2006\\", enviado por Leo"',
    },
    'tags': {'art3': ['#agricultura-familiar'], 'art1': ['#agricultura-familiar'], 'art4': ['#agricultura-familiar'], 'art5': ['#agricultura-familiar'], 'art2': ['#agricultura-familiar']},
    'relacao': [
        '- Fora do escopo ambiental da base. Incluída porque normas ambientais remetem ao conceito de agricultor familiar e empreendedor familiar rural do art. 3º, entre elas a [[lei-federal-12651-2012|Lei nº 12.651/2012]] (pequena propriedade ou posse rural familiar) e a [[lei-federal-11977-2009|Lei nº 11.977/2009]].',
        '- O art. 3º, inciso I, usa o módulo fiscal como critério de área (até 4 módulos fiscais), o mesmo da Lei nº 12.651/2012 para o regime diferenciado do imóvel rural.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
