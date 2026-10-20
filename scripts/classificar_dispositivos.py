"""Pré-classificação funcional auditável; não altera nem certifica o texto legal."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata

CATEGORIAS = {
    'enquadramento': 'Específicas para enquadramento',
    'licenciamento': 'Específicas para licenciamento',
    'obrigacoes-proibicoes': 'Obrigações e proibições',
    'limites-parametros': 'Limites de parâmetros',
    'normas-gerais': 'Normas gerais',
}
VERSAO = 'funcional/1'
# Cada regra procura a função do comando, não apenas o nome da norma.
REGRAS = {
    'enquadramento': [
        r'\benquadra\w*', r'\bcnae\b', r'\bpotencial poluidor\b',
        r'\bporte\b', r'\bbaixo (?:risco|impacto)\b',
        r'\b(?:dispensad\w*|isenta\w*|sujeit\w*)\b.{0,90}\blicenciamento\b',
        r'\b(?:licenciamento|licenca)\b.{0,70}\b(?:dispensad\w*|inexigivel|simplificad\w*)\b',
        r'\b(?:classificacao|tipologia)\b.{0,60}\b(?:atividad\w*|empreendimento\w*)\b',
    ],
    'licenciamento': [
        r'\blicenca\w* (?:previa|de instalacao|de operacao|ambiental|simplificada)\b',
        r'\b(?:requerimento|renovacao|emissao|concessao|solicitacao|indeferimento|suspensao|cancelamento)\b.{0,75}\blicenca\w*\b',
        r'\blicenciamento\b.{0,75}\b(?:procedimento|documento|estudo|prazo|etapa|competencia)\w*\b',
        r'\b(?:eia|rima|pca|pbca|rdpa|rce|ras|relatorio ambiental simplificado|termo de referencia)\b',
        r'\b(?:documentos|estudos)\b.{0,65}\b(?:apresentad\w*|exigid\w*|licenciamento)\b',
    ],
    'obrigacoes-proibicoes': [
        r'\b(?:devera\w*|devem|deve|obrigatori\w*|obrigad\w*|proibid\w*|vedad\w*)\b',
        r'\bnao (?:podera\w*|e permitido|serao permitid\w*|e admitid\w*)\b',
        r'\b(?:fica|ficam)\b.{0,25}\bresponsave\w*\b',
        r'\b(?:e|sao) permitid\w*\b.{0,40}\b(?:somente|apenas|desde que)\b',
    ],
    'limites-parametros': [
        r'\b(?:mg\s*/\s*[lnm]|[uµμ]g\s*/\s*[lm]|ng\s*/\s*m|g\s*/\s*nm|ppm|ppb|db\s*\(?a\)?|ntu|unt|nmp\s*/|ufc\s*/)\b',
        r'\b(?:ph|dbo|dqo|turbidez|oxigenio dissolvido|material particulado)\b.{0,75}\b\d',
        r'\b(?:limite\w*|padroes|padrao)\b.{0,80}\b(?:emissao|lancamento|qualidade|concentracao|ruido)\b',
        r'\b(?:temperatura|concentracao|eficiencia de remocao)\b.{0,65}\d',
    ],
}


def texto_limpo(texto):
    texto = re.sub(r'^Tags:.*$', '', texto, flags=re.M)
    texto = re.sub(r'^#{1,6}[^\n]*', '', texto, flags=re.M)
    texto = re.sub(r'\*\*[^*]+\*\*\s*\{#[^}]+\}', '', texto)
    texto = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', texto)
    texto = re.sub(r'\{#[^}]+\}|(?<!\w)#[a-z][\w-]*', '', texto)
    return ' '.join(texto.split())


def classificar(texto, contexto=''):
    proprio = texto_limpo(texto)
    normal = ''.join(c for c in unicodedata.normalize('NFKD', proprio.lower())
                     if not unicodedata.combining(c))
    motivos = {}
    for categoria, regras in REGRAS.items():
        sinais = [m.group(0) for regra in regras if (m := re.search(regra, normal))]
        if categoria == 'limites-parametros':
            # Mencionar padrões não fixa um limite; composição de produto
            # (CAS/concentração comercial) também não é padrão ambiental.
            if not re.search(r'\d', normal) or re.search(r'\bcas\b|produto comercial', normal):
                sinais = []
        if sinais:
            motivos[categoria] = list(dict.fromkeys(sinais))[:3]
    # Contexto só ajuda a interpretar uma linha técnica sem unidade repetida.
    if 'limites-parametros' not in motivos and re.search(r'\d', proprio):
        ctx = contexto.lower()
        if re.search(r'mg/|µg/|μg/|ppm|padr[oõ]es de (?:emiss|qualidade)', ctx) and not re.search(r'\bcas\b|produto comercial', normal):
            motivos['limites-parametros'] = ['Contexto técnico do pai; conferir unidade e cabeçalho']
    if not motivos:
        motivos['normas-gerais'] = ['Sem sinal funcional específico; classificação residual a conferir']
    return {'categorias': list(motivos), 'motivos': motivos,
            'estado': 'sugerida', 'metodo': VERSAO,
            'texto_sha256': hashlib.sha256(texto.encode('utf-8')).hexdigest()}


def aplicar(dispositivos, raiz):
    caminho = Path(raiz) / 'consultas/classificacao-revisada.json'
    revisoes = json.loads(caminho.read_text(encoding='utf-8')) if caminho.exists() else {}
    por_id = {d['chave']: d for d in dispositivos}
    desconhecidos = set(revisoes) - set(por_id)
    if desconhecidos:
        raise ValueError('Revisões com IDs inexistentes: ' + ', '.join(sorted(desconhecidos)[:5]))
    for d in dispositivos:
        if not d['elegivel']:
            continue
        pai = por_id.get(d.get('pai'), {})
        resultado = classificar(d['texto'], pai.get('texto', ''))
        revisao = revisoes.get(d['chave'])
        if revisao is not None:
            cats = revisao.get('categorias')
            if (not isinstance(cats, list) or not cats or
                    any(c not in CATEGORIAS for c in cats) or len(set(cats)) != len(cats)):
                raise ValueError('Categorias inválidas em ' + d['chave'])
            if revisao.get('texto_sha256') != resultado['texto_sha256']:
                # Não aplicar uma revisão humana feita sobre outra redação.
                resultado['revisao_desatualizada'] = True
            else:
                resultado.update(categorias=cats, estado='revisada',
                                 motivos={c: ['Revisão humana registrada'] for c in cats})
        d['funcao'] = resultado


def relatorio(dispositivos, commit):
    return {'formato': VERSAO, 'commit': commit, 'categorias': CATEGORIAS,
            'dispositivos': [{k: d[k] for k in ('chave', 'arquivo', 'linha_inicio',
                'linha_fim', 'texto', 'funcao')} for d in dispositivos if 'funcao' in d]}
