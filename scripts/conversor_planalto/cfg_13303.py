from make import *
import tagger

REGRAS = [
    (r'licitac', '#licitacao'),
    (r'contrat', '#contrato-administrativo'),
    (r'dispensa|inexigib|dispensavel', '#dispensa-licitacao'),
    (r'conselho de administracao|diretoria|administradores', '#governanca-corporativa'),
    (r'integridade|compliance|gestao de riscos|controle interno', '#integridade'),
    (r'fiscaliza|tribunais? de contas|controle externo', '#fiscalizacao'),
    (r'sustentabilidade ambiental|impacto ambiental|meio ambiente|licenciamento ambiental|ambient', '#sustentabilidade'),
    (r'penalidade|sanc|multa|advertencia|suspensao temporaria', '#sancao'),
    (r'prazo', '#prazo'),
]

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ', 'texto de dispositivo revogado'))]
    rem = getattr(pr, 'revogados_com_texto', [])
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (39 páginas, a última só com o rodapé), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 1º.7.2016" não transcritos.',
        '',
        '- O PDF não traz trechos tachados; as poucas alterações aparecem só nas anotações do Planalto.',
        '- Título II: "EMPRESAS PúBLICAS" com "ú" minúsculo no original; mantido.',
        '- Espaço antes da vírgula ou do ponto depois de algumas citações de lei ("de 2013 ,", "de 1997 ."), como no original; mantido.',
        '- Art. 96: revoga só dispositivos de outras leis (o § 2º do art. 15 da Lei nº 3.890-A/1961 e os arts. 67 e 68 da Lei nº 9.478/1997); por ser revogação parcial, as duas leis ficam em `altera`, conforme a lição de 27/09/2026.',
        '- Dispositivos vetados mantidos com o rótulo e "(VETADO)", como no original.',
    ]
    if rem:
        out.append('- Dispositivos publicados com texto e anotação de revogação: texto retirado (regra de 06/10/2026): ' + ', '.join(f'`{i}`' for i, _ in rem) + '.')
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'l13303', 'arquivo': 'lei-federal-13303-2016',
    'titulo': 'Lei Federal nº 13.303, de 30 de junho de 2016',
    'preambulo_re': r'^O VICE-PRESIDENTE',
    'niveis': {'TITULO': 2, 'CAPITULO': 3, 'SECAO': 4, 'SUBSECAO': 5},
    'revogado_remove_texto': True,
    'ementa_md': 'Dispõe sobre o estatuto jurídico da empresa pública, da sociedade de economia mista e de suas subsidiárias, no âmbito da União, dos Estados, do Distrito Federal e dos Municípios.',
    'cabecalho': 'Anotações do Planalto no cabeçalho: "Mensagem de veto", "Regulamento", "(Vide ADIN 5624)" e "(Vide [[lei-federal-14133-2021|Lei nº 14.133, de 2021]])".',
    'fm': {
        'norma': 'Lei Federal nº 13.303/2016', 'arquivo': 'lei-federal-13303-2016', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '13303', 'ano': '2016', 'data_assinatura': '2016-06-30', 'data_publicacao': '2016-07-01',
        'publicacao': 'Diário Oficial da União de 01/07/2016', 'vigencia': 'na data da publicação (art. 97), com prazos de adaptação (art. 91)',
        'orgao': 'Presidência da República',
        'ementa': '"Dispõe sobre o estatuto jurídico da empresa pública, da sociedade de economia mista e de suas subsidiárias, no âmbito da União, dos Estados, do Distrito Federal e dos Municípios."',
        'apelido': 'Lei das Estatais',
        'situacao': 'vigente', 'texto': 'compilado',
        'regulamenta': '[]', 'regulamentado_por': '[]',
        'altera': fm_list(['lei-federal-3890-a-1961', 'lei-federal-9478-1997']),
        'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Secretaria-Geral), impressão do navegador em PDF (Safari/iOS), 39 páginas; \\"Este texto não substitui o publicado no DOU de 1º.7.2016\\", enviado por Leo"',
    },
    'tags': tagger.por_regras(REGRAS),
    'relacao': [
        '- Regime próprio de licitações e contratos das empresas públicas e sociedades de economia mista (arts. 28 a 84). A [[lei-federal-14133-2021|Lei nº 14.133/2021]] não se aplica a elas, salvo o disposto no seu art. 178 (crimes) (art. 1º, § 1º, daquela Lei).',
        '- Para o licenciamento ambiental, interessa em especial o art. 32, § 1º (licitações e contratos devem respeitar normas de disposição final de resíduos, mitigação de impactos ambientais, condicionantes do licenciamento etc.).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
