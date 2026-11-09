from make import *

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith('inciso sem travessão')]
    st = [l for l in pr.log if l.startswith('inciso sem travessão')]
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto ("L13105compilada", 169 páginas), enviada por Leo. Cabeçalho institucional, links laterais ("Mensagem de veto", "Vigência", "Vide Lei nº 15.479, de 2026", "(Vide Lei nº 15.484, de 2026)", registrados no cabeçalho), o ícone de link antes de cada "Art." (caractere de uso privado da fonte) e o rodapé "Este texto não substitui o publicado no DOU de 17.3.2015" não transcritos.',
        '',
        '- Texto compilado: não foram detectados trechos tachados no PDF (PyMuPDF); as redações em vigor vêm com as anotações "(Redação dada ...)", "(Incluído ...)", "(Revogado ...)" e "(Vigência)" do Planalto.',
        '- Estrutura: o Código tem seis níveis de divisão (Parte, Livro, Título, Capítulo, Seção, Subseção) e o Markdown só tem quatro antes do artigo. A Parte entra no título do seu primeiro Livro ("PARTE GERAL – LIVRO I – ..."); Livro `##`, Título `###`, Capítulo `####`, Seção e Subseção `#####` (a Subseção fica no mesmo nível da Seção, logo depois dela).',
        '- Artigos com numeração de milhar ("Art. 1.015") têm ID sem o ponto (`art1015`) e rótulo com o ponto, como no original.',
        '- Arts. 1.060 a 1.071: as novas redações de outras leis estão em citação (`art1060_cpt_alt1` etc.), com o texto entre aspas e as linhas pontilhadas do original; os números de artigo dentro das citações são das leis alteradas e não viram links internos.',
        '- Vigência das alterações de 2026: as anotações "(Redação dada pela Lei nº 15.484, de 2026) Vigência" remetem à cláusula de vigência dessa lei, que entra em vigor 30 dias depois da publicação (art. 7º; DOU de 4/8/2026, edição extra), ou seja, já em vigor (fonte: Câmara dos Deputados, Legislação Informatizada, consultada em 09/11/2026). A vigência da Lei nº 15.479/2026, citada no cabeçalho, não foi conferida.',
        '- Links internos ligam o número do artigo (`art. [[#art311|311]]`), não o inciso citado.',
        '- Ordinais com "o" sobrescrito transcritos como "º" só nos rótulos; o texto segue o PDF.',
        '- Norma fora do escopo ambiental, incluída por ser citada por normas ambientais (substitui o CPC de 1973, citado pelo antigo Código Florestal e pela Lei nº 12.651/2012). Sem tags temáticas.',
    ]
    if st:
        out.append(f'- Incisos publicados sem travessão depois do número romano ({len(st)} casos), mantidos como no original: ' + '; '.join(x.split(': ', 1)[1] for x in st) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'cpc2015', 'arquivo': 'lei-federal-13105-2015',
    'titulo': 'Lei Federal nº 13.105, de 16 de março de 2015 – Código de Processo Civil',
    'preambulo_re': r'^A PRESIDENTA DA REPÚBLICA',
    'niveis': {'PARTE': 'prefixo', 'LIVRO': 2, 'TITULO': 3, 'CAPITULO': 4, 'SECAO': 5, 'SUBSECAO': 5},
    'ementa_md': 'Código de Processo Civil.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Mensagem de veto", "Vigência", "Vide [[lei-federal-15479-2026|Lei nº 15.479, de 2026]] Vigência" e "(Vide [[lei-federal-15484-2026|Lei nº 15.484, de 2026]]) Vigência" (links do portal).',
    'fm': {
        'norma': 'Lei Federal nº 13.105/2015', 'arquivo': 'lei-federal-13105-2015', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '13105', 'ano': '2015', 'data_assinatura': '2015-03-16', 'data_publicacao': '2015-03-17',
        'publicacao': 'Diário Oficial da União de 17/03/2015', 'vigencia': '1 (um) ano após a publicação (art. 1.045)',
        'orgao': 'Presidência da República',
        'ementa': '"Código de Processo Civil."',
        'apelido': 'Código de Processo Civil (CPC/2015)',
        'situacao': 'vigente', 'texto': 'compilado (atualizado até a mais recente alteração anotada no PDF)',
        'regulamenta': '[]', 'regulamentado_por': '[]',
        'altera': fm_list(['decreto-lei-federal-25-1937', 'lei-federal-1060-1950', 'lei-federal-4737-1965', 'lei-federal-5478-1968', 'lei-federal-6015-1973',
                           'lei-federal-8038-1990', 'lei-federal-9099-1995', 'lei-federal-9289-1996', 'lei-federal-9307-1996', 'lei-federal-10406-2002', 'lei-federal-12529-2011']),
        'revoga': '["[[lei-federal-5869-1973]]"]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Secretaria-Geral), impressão do navegador em PDF do texto compilado, 169 páginas; \\"Este texto não substitui o publicado no DOU de 17.3.2015\\", enviado por Leo"',
    },
    'cita_extra': ['lei-federal-15479-2026', 'lei-federal-15484-2026', 'lei-federal-5869-1973'],
    'tags': {},
    'assinaturas': lambda a: ['DILMA ROUSSEFF', 'José Eduardo Cardozo', 'Jaques Wagner', 'Joaquim Vieira Ferreira Levy', 'Luís Inácio Lucena Adams'],
    'relacao': [
        '- Fora do escopo ambiental da base. Revogou o Código de Processo Civil de 1973 ([[lei-federal-5869-1973|Lei nº 5.869/1973]]), art. 1.046; as remissões de normas antigas ao CPC/1973 passam a valer para os dispositivos correspondentes deste Código (art. 1.046, § 4º).',
        '- O procedimento sumário do art. 275 do CPC/1973 (a que remetia o art. 1º, § 1º, da [[lei-federal-4771-1965|Lei nº 4.771/1965]]) não existe neste Código: as ações passam ao procedimento comum (art. 1.049, parágrafo único).',
        '- Arts. 1.060 a 1.072: alteram e revogam em parte outras leis (Lei de Arbitragem, Lei dos Juizados Especiais, Código Eleitoral, Código Civil, Lei de Registros Públicos e outras), nenhuma delas na base; registradas em `altera`.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
