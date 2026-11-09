from make import *

def notas(rd, pr, drop):
    log = [l for l in pr.log]
    return [
        'Fonte: impressão em PDF do texto do Planalto ("L4771impressao", 11 páginas), enviada por Leo. Cabeçalho institucional, links laterais ("Mensagem de veto", "Vigência") e o rodapé "Este texto não substitui o publicado no DOU de 16.9.1965 e retificado em 28.9.65" não transcritos.',
        '',
        '- Lei revogada por inteiro pela [[lei-federal-12651-2012|Lei nº 12.651/2012]] (anotação do Planalto no cabeçalho: "Revogada pela Lei nº 12.651, de 2012."). Transcrita porque normas da base ainda remetem a ela (arts. 2º, 16, 44, 44-A e 44-B). O texto é o compilado até a revogação.',
        '- A versão "impressão" do Planalto não traz trechos tachados (redações anteriores): não foram detectados traços de tachado no PDF (PyMuPDF). Só a última redação de cada dispositivo foi transcrita, com as anotações "(Redação dada ...)", "(Incluído ...)", "(Revogado ...)", "(Renumerado ...)" e "(Vide ...)" do Planalto.',
        '- Ordinais: o PDF mistura "º", "°" e "o" sobrescrito ("Art. 1°", "§ 1o"); mantidos no texto como publicados e normalizados para "º" só nos rótulos.',
        '- Grafias da época ("cinqüenta", "seqüência", "moto-serras", "micro-bacia") mantidas.',
        '- Art. 39: não consta do PDF (o texto passa do art. 38, revogado pela Lei nº 5.868/1972, ao art. 40, vetado); não foi criado ID para ele.',
        '- Art. 26: alíneas "j" e "l" seguidas, sem "k" (alfabeto da época); mantidas.',
        '- Assinaturas: o PDF imprime os quatro nomes em sequência; separados um por linha.',
    ] + ([f'- Conferência automática do parser: {"; ".join(log)}.'] if log else [])

cfg = {
    'json': 'l4771', 'arquivo': 'lei-federal-4771-1965',
    'titulo': 'Lei Federal nº 4.771, de 15 de setembro de 1965',
    'preambulo_re': r'^O PRESIDENTE',
    'niveis': {},
    'ementa_md': 'Institui o novo Código Florestal.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Mensagem de veto", "Vigência", "(Vide [[lei-federal-8847-1994|Lei nº 8.847 de 1994]])" e "Revogada pela [[lei-federal-12651-2012|Lei nº 12.651, de 2012]]."',
    'fm': {
        'norma': 'Lei Federal nº 4.771/1965', 'arquivo': 'lei-federal-4771-1965', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '4771', 'ano': '1965', 'data_assinatura': '1965-09-15', 'data_publicacao': '1965-09-16',
        'publicacao': 'Diário Oficial da União de 16/09/1965 (retificado em 28/09/1965)', 'vigencia': '120 dias após a publicação (art. 50); revogada pela Lei nº 12.651/2012',
        'orgao': 'Presidência da República',
        'ementa': '"Institui o novo Código Florestal."',
        'apelido': 'Código Florestal de 1965 (revogado)',
        'situacao': 'revogada', 'texto': 'compilado até a revogação (última alteração anotada: Lei nº 11.934/2009)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '["[[decreto-federal-23793-1934]]"]', 'revogado_por': '["[[lei-federal-12651-2012]]"]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF (versão de impressão), 11 páginas; \\"Este texto não substitui o publicado no DOU de 16.9.1965 e retificado em 28.9.65\\", enviado por Leo"',
    },
    'cita_extra': ['lei-federal-8847-1994', 'lei-federal-12651-2012', 'decreto-federal-23793-1934'],
    'manual': [('previsto no art. 275, inciso II, do Código de Processo Civil', 'previsto no [[lei-federal-5869-1973#art275_cpt_inc2|art. 275, inciso II, do Código de Processo Civil]]')],
    'tags': {},
    'assinaturas': lambda a: ['H. CASTELLO BRANCO', 'Hugo Leme', 'Octavio Gouveia de Bulhões', 'Flávio Lacerda'],
    'relacao': [
        '- Revogada pela [[lei-federal-12651-2012|Lei nº 12.651/2012]] (novo Código Florestal), art. 83. Mantida na base como texto histórico, porque normas anteriores a 2012 e atos ainda em curso remetem a ela (APP do art. 2º, reserva legal dos arts. 16 e 44, servidão florestal do art. 44-A e Cota de Reserva Florestal do art. 44-B). Para a regra em vigor, consultar a Lei nº 12.651/2012 (APP: arts. 4º a 9º; reserva legal: arts. 12 a 25; servidão ambiental e CRA: arts. 44 a 50) (correspondência do conversor, não está no PDF).',
        '- O § 1º do art. 1º remete ao procedimento sumário do [[lei-federal-5869-1973#art275_cpt_inc2|art. 275, II, do CPC de 1973]], também revogado (pela [[lei-federal-13105-2015|Lei nº 13.105/2015]]).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
