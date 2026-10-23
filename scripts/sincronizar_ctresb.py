#!/usr/bin/env python3
"""Importa um recorte explícito de um commit Git, sem alterar normas/.
Uso: python scripts/sincronizar_ctresb.py ../ctresb-leis [--ref COMMIT]
O índice versionado permite build e consulta sem rede. Atualizações são revisadas em PR.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ('reguladores/conama/resolucoes/', 'reguladores/ibama/instrucoes-normativas/')
REPO = 'leoparreira21/ctresb-leis'
ARTICLE = re.compile(r'^\s*(?:\*\*)?Art\.\s*(\d+(?:-[A-Za-z])?)(?:[º°o.]|\*\*|\s)', re.I)


def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFD', str(value).lower()) if not unicodedata.combining(c))


def metadata(text):
    if not text.startswith('---\n'):
        raise ValueError('Cabeçalho ausente')
    header, _ = text[4:].split('\n---\n', 1)
    result = {}
    for line in header.splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        value = value.strip()
        if value.startswith('"'):
            value = json.loads(value)
        result[key] = value
    return result


def identity(m, org):
    number = re.sub(r'\D', '', str(m.get('numero', '')))
    year = str(m.get('data', m.get('data_assinatura', m.get('ano', ''))))[:4]
    kind = 'instrucao-normativa' if 'instruc' in norm(m.get('tipo', '')) else 'resolucao'
    return f'{kind}-{org}-{int(number)}-{year}' if number and re.fullmatch(r'\d{4}', year) else None


def parse(text, path, commit):
    m = metadata(text)
    if norm(m.get('revogada', '')) == 'true' or re.search(r'\brevogad[ao]\b', norm(m.get('situacao', ''))):
        return None, 'revogada'
    org = path.split('/')[1]
    key = identity(m, org)
    if not key:
        return None, 'identidade_incompleta'
    lines = text.splitlines()
    starts = [(i, ARTICLE.match(line)) for i, line in enumerate(lines) if ARTICLE.match(line)]
    if not starts:
        return None, 'sem_artigos'
    # Numeração repetida pode ser texto alterador citado ou redações concorrentes.
    ids = [match[1].lower() for _, match in starts]
    if len(ids) != len(set(ids)):
        return None, 'artigos_ambiguos'
    articles = []
    for pos, (begin, match) in enumerate(starts):
        end = starts[pos+1][0] if pos+1 < len(starts) else len(lines)
        # Anexos permanecem na íntegra de origem, nunca atribuídos ao último artigo.
        for j in range(begin+1, end):
            if re.match(r'^\s*(?:#+\s*|\*\*)?ANEXO\b', lines[j], re.I):
                end = j
                break
        body = '\n'.join(lines[begin:end]).strip()
        if '~~' in body or re.search(r'<\s*(?:s|del|strike)\b', body, re.I):
            continue  # não promover redação histórica a comando atual
        articles.append({'id': 'art'+match[1].lower(), 'texto': body,
                         'linhas': [begin+1, end]})
    if not articles:
        return None, 'sem_artigos_seguros'
    summary = next((line for line in lines[:starts[0][0]] if re.match(r'^(Dispõe|Estabelece|Regulamenta|Altera|Institui)\b', line)), '')
    return {'id': key, 'titulo': m['titulo'], 'ementa': m.get('ementa', summary), 'arquivo': path, 'orgao': org,
            'fonte_oficial': m.get('fonte', ''), 'versao_texto': m.get('versao_texto', ''),
            'situacao_fonte': m.get('situacao', 'não informada'), 'vigencia': 'nao_verificada',
            'sha256': hashlib.sha256(text.encode()).hexdigest(),
            'url': f'https://github.com/{REPO}/blob/{commit}/{path}',
            'artigos': articles}, None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repositorio', type=Path)
    p.add_argument('--ref', default='HEAD')
    args = p.parse_args()
    def git(*cmd):
        return subprocess.check_output(['git', '-C', str(args.repositorio), *cmd], text=True)
    commit = git('rev-parse', '--verify', args.ref+'^{commit}').strip()
    paths = git('ls-tree', '-r', '--name-only', commit, *PREFIXES).splitlines()
    if not paths:
        raise ValueError('Recorte vazio; índice anterior preservado')
    local = {path.stem for path in (ROOT/'normas').glob('*.md')}
    docs, omitted, seen = [], [], set()
    for path in sorted(paths):
        if not path.endswith('.md'):
            continue
        text = git('show', commit+':'+path)
        doc, reason = parse(text, path, commit)
        if doc and doc['id'] in local:
            reason = 'ja_existe_na_base_curada'
        if doc and doc['id'] in seen:
            reason = 'identidade_ambigua'
            for previous in docs:
                if previous['id'] == doc['id']:
                    omitted.append({'arquivo': previous['arquivo'], 'motivo': reason})
            docs = [d for d in docs if d['id'] != doc['id']]
        if reason:
            omitted.append({'arquivo': path, 'motivo': reason})
        else:
            seen.add(doc['id'])
            docs.append(doc)
    result = {'formato': 'complementar/1', 'repositorio': REPO, 'commit': commit,
              'recorte': list(PREFIXES), 'documentos': docs, 'omitidos': omitted}
    encoded = json.dumps(result, ensure_ascii=False, separators=(',', ':'))+'\n'
    if len(encoded.encode()) > 8_000_000:
        raise ValueError('Índice excede 8 MB; reduza o recorte ou implemente fragmentação')
    target = ROOT/'consultas/ctresb-index.json'
    target.with_suffix('.tmp').write_text(encoded, encoding='utf-8')
    target.with_suffix('.tmp').replace(target)
    print(f'{len(docs)} normas; {sum(len(d["artigos"]) for d in docs)} artigos; {len(omitted)} omitidas; {len(encoded.encode())} bytes; {commit}')


if __name__ == '__main__':
    main()
