from make import *

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('inciso sem travessão', 'numeral do inciso', 'Art. ', '"S eção'))]
    st = [l for l in pr.log if l.startswith('inciso sem travessão')]
    out = [
        'Fonte: impressão em PDF do texto do Planalto ("L5869impressao", 95 páginas), enviada por Leo. Cabeçalho institucional, links laterais ("Vigência", "(Revogada pela Lei nº 13.105, de 2015) (Vigência)", "(Vide Lei nº 9.245, de 1995)", registrados no cabeçalho) e o rodapé "Este texto não substitui o publicado no DOU de 17.1.1973 e republicado em 27.7.2006" não transcritos.',
        '',
        '- Lei revogada por inteiro pela [[lei-federal-13105-2015|Lei nº 13.105/2015]] (novo CPC, art. 1.046), em vigor desde março de 2016. Transcrita porque normas da base ainda remetem a ela (procedimento sumário do art. 275, II, citado pela Lei nº 4.771/1965 e pela Lei nº 12.651/2012). O texto é o compilado até a revogação.',
        f'- A versão "impressão" do Planalto quase não traz trechos tachados: só {len(drop)} parágrafo(s) tachado(s) foram detectados (PyMuPDF) e omitidos. As redações vêm com as anotações "(Redação dada ...)", "(Incluído ...)", "(Revogado ...)" e "(Renumerado ...)" do Planalto.',
        '- Ordinais: o "o" sobrescrito ("Art. 1o", "§ 2o", "Lei no") sai da camada de texto deslocado; foi recolocado junto ao número pela posição (PyMuPDF) e transcrito como "o", como no PDF; nos rótulos, "º".',
        '- Arts. 1.102.a e 1.102.b (ação monitória): numerados com ponto e letra minúscula no original, ao lado do "Art. 1.102-C"; mantidos como publicados nos rótulos, com IDs `art1102-a`, `art1102-b` e `art1102-c`.',
        '- Estrutura: Livro `##`, Título `###`, Capítulo `####`, Seção e Subseção `#####` (a Subseção fica no mesmo nível da Seção, logo depois dela).',
        '- Links internos ligam o número do artigo, não o inciso citado.',
        '- Art. 563: não consta do PDF (o texto passa do art. 562 ao art. 564, sem anotação); não foi criado ID para ele. Conferir na publicação oficial se necessário.',
        '- Art. 217, inciso I: o PDF traz "I - (Revogado pela Lei nº 8.952, de 13.12.1994)" seguido de "I - a quem estiver assistindo a qualquer ato de culto religioso; (Inciso II renumerado ...)". Ficou só o inciso I atual (renumerado); a revogação do inciso I original consta só desta nota.',
        '- Numerais romanos com a letra "l" no lugar do "I" ("Vl", "Il", "Vll", "Vlll", "Xl", "Ill") e com espaço ("I I", "I II") no original: lidos como VI, II etc. nos rótulos e IDs; o "S eção III" (Livro I, antes do art. 331) foi lido como "Seção III".',
        '- Vários artigos revogados impressos num mesmo parágrafo ("Art. 430. (Revogado ...) Art. 431. (Revogado ...)", arts. 1.072 a 1.102, juízo arbitral): separados, um ID por artigo. Nos arts. 1.072 a 1.102 a anotação vem sem parênteses ("Revogado pela Lei nº 9.307, de 23.9.1996:") e foi tratada como anotação de revogação.',
        '- Caracteres soltos no alto das páginas (restos da linha cortada na quebra de página, ex.: "j g" antes do art. 679) descartados.',
        '- Art. 1.220: "revogadas as disposições em contrário" (revogação tácita, sem lista); nada foi marcado como revogado em outras normas.',
        '- Norma fora do escopo ambiental, incluída por ser citada por normas ambientais. Sem tags temáticas.',
    ]
    if st:
        out.append(f'- Incisos publicados sem travessão depois do número romano ({len(st)} casos), mantidos como no original.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'cpc1973', 'arquivo': 'lei-federal-5869-1973',
    'titulo': 'Lei Federal nº 5.869, de 11 de janeiro de 1973 – Código de Processo Civil (revogado)',
    'preambulo_re': r'^O PRESIDENTE DA REPÚBLICA',
    'niveis': {'LIVRO': 2, 'TITULO': 3, 'CAPITULO': 4, 'SECAO': 5, 'SUBSECAO': 5},
    'art_letra_ponto': True,
    'fix': lambda t: t.replace('§ 1o -A Se a decisão', '§ 1o-A Se a decisão'),
    'ementa_md': 'Institui o Código de Processo Civil.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Vigência", "(Revogada pela [[lei-federal-13105-2015|Lei nº 13.105, de 2015]]) (Vigência)" e "(Vide [[lei-federal-9245-1995|Lei nº 9.245, de 1995]])".',
    'fm': {
        'norma': 'Lei Federal nº 5.869/1973', 'arquivo': 'lei-federal-5869-1973', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '5869', 'ano': '1973', 'data_assinatura': '1973-01-11', 'data_publicacao': '1973-01-17',
        'publicacao': 'Diário Oficial da União de 17/01/1973 (republicado em 27/07/2006)', 'vigencia': '1º de janeiro de 1974 (art. 1.220); revogada pela Lei nº 13.105/2015',
        'orgao': 'Presidência da República',
        'ementa': '"Institui o Código de Processo Civil."',
        'apelido': 'Código de Processo Civil de 1973 (revogado)',
        'situacao': 'revogada', 'texto': 'compilado até a revogação',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '["[[lei-federal-13105-2015]]"]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF (versão de impressão), 95 páginas; \\"Este texto não substitui o publicado no DOU de 17.1.1973 e republicado em 27.7.2006\\", enviado por Leo"',
    },
    'cita_extra': ['lei-federal-13105-2015', 'lei-federal-9245-1995'],
    'tags': {},
    'assinaturas': lambda a: ['EMÍLIO G. MÉDICI', 'Alfredo Buzaid'],
    'relacao': [
        '- Revogada pela [[lei-federal-13105-2015|Lei nº 13.105/2015]] (art. 1.046). As remissões de outras leis a este Código passam a valer para os dispositivos correspondentes do CPC/2015 ([[lei-federal-13105-2015#art1046_par4|art. 1.046, § 4º]]); a remissão ao procedimento sumário vira procedimento comum ([[lei-federal-13105-2015#art1049_par1u|art. 1.049, parágrafo único]]).',
        '- O [[#art275_cpt_inc2|art. 275, II]] (procedimento sumário) é citado pelo art. 1º, § 1º, da [[lei-federal-4771-1965|Lei nº 4.771/1965]] e pela [[lei-federal-12651-2012|Lei nº 12.651/2012]].',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
