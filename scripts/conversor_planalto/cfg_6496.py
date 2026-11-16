from make import *

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ',))]
    out = [
        'Fonte: impressão em PDF do texto do Planalto (3 páginas), enviada por Leo. Cabeçalho institucional e o rodapé "Este texto não substitui o publicado no DOU de 9.12.1977" não transcritos; as anotações "Vide" do cabeçalho ficam registradas acima do preâmbulo.',
        '',
        '- A impressão não traz trechos tachados nem anotações de alteração no corpo: a Lei tem só as três remissões "Vide" do cabeçalho.',
        '- Artigos escritos "Art 1º -" (sem ponto depois de "Art" e com travessão), incisos com "-" e parágrafos com "§ 1º -"; mantidos como publicados.',
        '- Numerais romanos impressos com "l" minúsculo no lugar do segundo "I" no original do Planalto (conferido na imagem da página): "Il" (art. 11, II; art. 14, II) e "Ill" (art. 13, III). O marcador foi lido como "II" e "III" para gerar o ID e o rótulo do inciso (`art11_cpt_inc2`, `art13_cpt_inc3`, `art14_cpt_inc2`); o marcador em si não faz parte do texto do dispositivo.',
        '- Art. 13, V: "peIa Mútua" (com "I" maiúsculo no lugar de "l") no original; mantido como publicado.',
        '- Art. 11, II: "CREAS" em maiúsculas (e "CREAs" nos demais artigos), como no original.',
        '- Fecho sem a vírgula final depois de "República" e com o ano da Independência e da República como publicados ("156º da Independência e 89º da República").',
        '- Assinaturas: o PDF imprime os dois nomes em sequência; separados um por linha.',
    ]
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

def fix(t):
    t = re.sub(r'^(\s*)Il\b', r'\1II', t)
    t = re.sub(r'^(\s*)Ill\b', r'\1III', t)
    return t

cfg = {
    'json': 'l6496', 'arquivo': 'lei-federal-6496-1977',
    'titulo': 'Lei Federal nº 6.496, de 7 de dezembro de 1977',
    'preambulo_re': r'^O PRESIDENTE',
    'fecho_re': r'^Brasília',
    'niveis': {}, 'fix': fix,
    'ementa_md': 'Institui a "Anotação de Responsabilidade Técnica" na prestação de serviços de engenharia, de arquitetura e agronomia; autoriza a criação, pelo Conselho Federal de Engenharia, Arquitetura e Agronomia - CONFEA, de uma Mútua de Assistência Profissional; e dá outras providências.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "(Vide [[lei-federal-6994-1982|Lei nº 6.994, de 1982]])", "(Vide [[decreto-federal-88147-1983|Decreto nº 88.147, de 1983]])" e "(Vide [[lei-federal-12378-2010|Lei nº 12.378, de 2010]])".',
    'fm': {
        'norma': 'Lei Federal nº 6.496/1977', 'arquivo': 'lei-federal-6496-1977', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '6496', 'ano': '1977', 'data_assinatura': '1977-12-07', 'data_publicacao': '1977-12-09',
        'publicacao': 'Diário Oficial da União de 09/12/1977', 'vigencia': 'na data da publicação (art. 20)',
        'orgao': 'Presidência da República',
        'ementa': '"Institui a \\"Anotação de Responsabilidade Técnica\\" na prestação de serviços de engenharia, de arquitetura e agronomia; autoriza a criação, pelo Conselho Federal de Engenharia, Arquitetura e Agronomia - CONFEA, de uma Mútua de Assistência Profissional; e dá outras providências."',
        'apelido': 'Lei da ART (Anotação de Responsabilidade Técnica)',
        'situacao': 'vigente', 'texto': 'compilado (sem alterações anotadas no corpo)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF, 3 páginas; \\"Este texto não substitui o publicado no DOU de 9.12.1977\\", enviado por Leo"',
    },
    'cita_extra': ['lei-federal-6994-1982', 'decreto-federal-88147-1983', 'lei-federal-12378-2010', 'lei-federal-5194-1966'],
    'manual': [('alínea " a " do art. 73 da Lei nº 5.194, de 24 de dezembro de 1966', '[[lei-federal-5194-1966#art73|alínea " a " do art. 73 da Lei nº 5.194, de 24 de dezembro de 1966]]')],
    'tags': {},
    'assinaturas': lambda a: ['ERNESTO GEISEL', 'Arnaldo Prieto'],
    'relacao': [
        '- Os arts. 1º a 3º instituem a ART (Anotação de Responsabilidade Técnica), que as normas de licenciamento da base exigem dos responsáveis técnicos de projetos e estudos de engenharia, arquitetura e agronomia; o art. 3º remete à multa do art. 73, alínea "a", da [[lei-federal-5194-1966#art73|Lei nº 5.194/1966]]. Os arts. 4º a 19 tratam da Mútua de Assistência dos Profissionais do sistema CONFEA/CREA e não interessam ao licenciamento.',
        '- O cabeçalho do Planalto traz "Vide Lei nº 12.378, de 2010" (lei do exercício da arquitetura e urbanismo e do Conselho de Arquitetura e Urbanismo). Segundo informação do conversor (não está no PDF), a ART é a anotação dos profissionais do sistema CONFEA/CREA; os arquitetos e urbanistas registram a responsabilidade técnica no CAU (RRT).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
