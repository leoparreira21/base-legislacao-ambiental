from make import *

def notas(rd, pr, drop):
    log = [l for l in pr.log if not l.startswith(('anotação ',))]
    out = [
        'Fonte: impressão em PDF do texto compilado do Planalto (18 páginas), enviada por Leo. Cabeçalho institucional e o rodapé "Este texto não substitui o publicado no DOU de 20.12.1979" não transcritos.',
        '',
        '- Trechos tachados no PDF (redações anteriores, %d parágrafos): não transcritos, conforme a decisão de 06/10/2026 (a base guarda só o texto em vigor). O texto anterior continua no PDF e no histórico do Planalto.' % len(drop),
        '- Ordinais com "o" sobrescrito transcritos como "º".',
        '- Numerais de incisos impressos "Il" (letra "l" no lugar do segundo "I") no original, lidos como II para gerar o ID e o rótulo: `art3_par1u_inc2`, `art9_par1_inc2` e `art13_cpt_inc2`. O marcador não faz parte do texto do dispositivo.',
        '- Art. 4º, inciso III, e inciso III-A: a anotação do inciso III-A está impressa "(Redação dada Lei nº 14.285, de 2021)", sem "pela"; mantida como publicada.',
        '- Linhas "Pena: ..." dos arts. 50 e 52 (sem marcador no original) ficam unidas ao inciso ou ao caput que as precede.',
        '- Fragmentos de texto tachado que o PDF deixou fora do tachado (por exemplo "2o 3o-A no 2o" depois do caput do art. 12 e um trecho "art. 108 da Lei nº 10.406 ... § 3o" no art. 26) foram descartados com o resto da redação tachada.',
        '- Marcações "(Vigência)" e "Vigência encerrada" do Planalto (ligadas às medidas provisórias que alteraram os arts. 12 e 26 e já perderam a eficácia) não transcritas; as redações das medidas provisórias estão tachadas no PDF e também ficaram fora.',
        '- Dispositivos vetados mantidos com o rótulo e "(VETADO)", como no original (art. 2º, § 3º; art. 51, parágrafo único).',
    ]
    if log:
        out.append('- Conferência automática da numeração: ' + '; '.join(log) + '.')
    return out

cfg = {
    'json': 'l6766', 'arquivo': 'lei-federal-6766-1979',
    'titulo': 'Lei Federal nº 6.766, de 19 de dezembro de 1979',
    'preambulo_re': r'^O PRESIDENTE',
    'fecho_re': r'^Brasília',
    'niveis': {'CAPITULO': 2},
    'ementa_md': 'Dispõe sobre o Parcelamento do Solo Urbano e dá outras Providências.',
    'fm': {
        'norma': 'Lei Federal nº 6.766/1979', 'arquivo': 'lei-federal-6766-1979', 'tipo': 'lei', 'esfera': 'federal',
        'numero': '6766', 'ano': '1979', 'data_assinatura': '1979-12-19', 'data_publicacao': '1979-12-20',
        'publicacao': 'Diário Oficial da União de 20/12/1979', 'vigencia': 'na data da publicação (art. 54)',
        'orgao': 'Presidência da República',
        'ementa': '"Dispõe sobre o Parcelamento do Solo Urbano e dá outras Providências."',
        'apelido': 'Lei do Parcelamento do Solo Urbano (Lei Lehmann)',
        'situacao': 'vigente', 'texto': 'compilado',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]', 'revogado_por': '[]',
        'fonte': '"Planalto (Presidência da República – Casa Civil), impressão do navegador em PDF, 18 páginas; \\"Este texto não substitui o publicado no DOU de 20.12.1979\\", enviado por Leo"',
    },
    'excluir': lambda texts: {i for i, t in enumerate(texts) if t == '2o 3o-A no 2o' or t.startswith('art. 108 da Lei nº 10.406, de 10 de janeiro de 2002 - Código Civil. § 3o')},
    'tags': {},
    'assinaturas': lambda a: ['JOÃO FIGUEIREDO', 'Petrônio Portella', 'Angelo Amaury Stábile', 'Mário David Andreazza'],
    'relacao': [
        '- Lei geral do parcelamento do solo urbano (loteamento e desmembramento). O art. 3º só admite o parcelamento em zonas urbanas, de expansão urbana ou de urbanização específica, e o seu parágrafo único o proíbe em terrenos alagadiços, aterrados com material nocivo, com declividade igual ou superior a 30%, com condições geológicas que não aconselham a edificação e em áreas de preservação ecológica ou de poluição sem correção; o art. 4º fixa os requisitos mínimos do loteamento e as faixas não edificáveis; o art. 12 submete o projeto à aprovação da Prefeitura; o art. 13 atribui aos Estados disciplinar a aprovação pelos Municípios nos casos que enumera (áreas de interesse especial, como a proteção de mananciais; áreas limítrofes ou metropolitanas; loteamento acima de 1.000.000 m²); o art. 53 exige audiência prévia do INCRA para alterar o uso do solo rural para fins urbanos (resumo do conversor, não é texto normativo).',
        '- O art. 4º, incisos III-A e III-B, incluídos pela [[lei-federal-14285-2021|Lei nº 14.285/2021]], tratam das faixas não edificáveis ao longo de ferrovias e de águas correntes e dormentes, que a lei municipal ou distrital do instrumento de planejamento territorial regulamenta. A mesma Lei nº 14.285/2021 alterou a [[lei-federal-12651-2012|Lei nº 12.651/2012]] (ver o conceito de "área urbana consolidada" no art. 3º, XXVI, dessa Lei). O art. 4º, § 3º, remete ao licenciamento ambiental a reserva de faixa não edificável vinculada a dutovias.',
        '- Citada por normas da base, entre elas as INs IAT 17/2025, 19/2025, 21/2025, 33/2025 e 35/2026, a Resolução SEDEST 30/2022 e a [[lei-federal-11445-2007|Lei nº 11.445/2007]] (que alterou o art. 2º, § 5º, da Lei nº 6.766/1979).',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
