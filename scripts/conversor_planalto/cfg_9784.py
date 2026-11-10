from make import *
import tagger

REGRAS = [
    (r'recurso administrativo|\brecurso\b', '#recurso-administrativo'),
    (r'\bprazos?\b', '#prazo'),
    (r'intimac', '#intimacao'),
    (r'impediment|suspeic', '#impedimento-suspeicao'),
    (r'delegac|avocac', '#delegacao-competencia'),
    (r'decisao coordenada', '#decisao-coordenada'),
    (r'consulta publica|audiencia publica', '#participacao-publica'),
    (r'motivad|motivacao', '#motivacao'),
    (r'anula|revoga|convalid', '#invalidacao-ato'),
    (r'decai|decadencia', '#decadencia'),
    (r'prova|instrucao', '#instrucao-processual'),
    (r'medidas? acauteladora|cautelar', '#medida-cautelar'),
    (r'prioridade na tramitacao', '#prioridade-tramitacao'),
]
EXTRA = {f'art{n}': ['#processo-administrativo'] for n in (1, 2, 5, 22, 69)}

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ',))]
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (15 páginas, a última só com o rodapé), feita no Safari do iOS, enviada por Leo. Cabeçalho institucional, rodapé de cada página (endereço do portal, data e hora, "Página X de Y") e o rodapé "Este texto não substitui o publicado no DOU de 1.2.1999 e retificado em 11.3.1999" não transcritos.',
        '',
        '- O PDF não traz trechos tachados (redações anteriores); as alterações aparecem só nas anotações "(Incluído pela Lei nº ...)". A Lei não teve dispositivos com nova redação anotada.',
        '- Ordinais com "o" sobrescrito transcritos como "º".',
        '- Fecho publicado sem vírgula depois de "Brasília" ("Brasília 29 de janeiro de 1999"); mantido.',
        '- Dispositivos vetados mantidos com o rótulo e "(VETADO)", como no original.',
    ]
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'l9784', 'arquivo': 'lei-federal-9784-1999',
    'titulo': 'Lei Federal nº 9.784, de 29 de janeiro de 1999',
    'preambulo_re': r'^O PRESIDENTE',
    'fecho_re': r'^Brasília',
    'niveis': {'CAPITULO': 2},
    'ementa_md': 'Regula o processo administrativo no âmbito da Administração Pública Federal.',
    'fm': {
        'norma': 'Lei Federal nº 9.784/1999', 'arquivo': 'lei-federal-9784-1999', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '9784', 'ano': '1999', 'data_assinatura': '1999-01-29', 'data_publicacao': '1999-02-01',
        'publicacao': 'Diário Oficial da União de 01/02/1999 (retificado em 11/03/1999)', 'vigencia': 'na data da publicação (art. 70)',
        'orgao': 'Presidência da República',
        'ementa': '"Regula o processo administrativo no âmbito da Administração Pública Federal."',
        'apelido': 'Lei do Processo Administrativo Federal',
        'situacao': 'vigente', 'texto': 'compilado (última alteração anotada: Lei nº 14.210/2021)',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF (Safari/iOS), 15 páginas; \\"Este texto não substitui o publicado no DOU de 1.2.1999 e retificado em 11.3.1999\\", enviado por Leo"',
    },
    'tags': tagger.por_regras(REGRAS, extra=EXTRA),
    'relacao': [
        '- Lei geral do processo administrativo federal. No processo de apuração de infrações ambientais, aplica-se subsidiariamente ao [[decreto-federal-6514-2008|Decreto nº 6.514/2008]], que a cita no preâmbulo (art. 69 desta Lei: os processos específicos continuam regidos por lei própria).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
