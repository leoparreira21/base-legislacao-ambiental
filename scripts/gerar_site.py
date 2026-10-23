#!/usr/bin/env python3
"""Gera o site de busca (pasta _site/) a partir das normas da base.

Uso: python scripts/gerar_site.py [pasta_de_saida]

O site é estático: site/index.html + motor de busca (site/motor.js) + índice
gerado aqui + tabela CNAE do IBGE (site/cnae.json) + consultas/sinonimos.json e
consultas/ambitos.json. manifesto.json resume a publicação (commit, versão do
motor e formato do índice) para clientes da busca, como a API do iatreports.
Roda no GitHub Actions a cada push na main (.github/workflows/site.yml).
Somente biblioteca padrão.
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'scripts'))
import consultar  # noqa: E402
import gerar_grafo  # noqa: E402
from classificar_dispositivos import relatorio

TAG = re.compile(r'(?<![\w/&])#([a-z0-9][a-z0-9-]+)')
MOTOR_VERSAO = re.compile(r"^export const MOTOR_VERSAO = '([^']+)';", re.M)
FORMATO_INDICE = re.compile(r'^export const FORMATO_INDICE = (\d+);', re.M)
PREFIXO_ANEXO = re.compile(r'^-\s*Anexo\b[^\n]*?(?:linha \d+|cabeçalho)\s*', re.M)


def limpar(t):
    t = re.sub(r'^Tags:.*$', '', t, flags=re.M)
    t = re.sub(r'\*\*Art\. [\w-]+º?, caput\*\*\s*', '', t)
    t = re.sub(r'\*\*Art\. [\w-]+º?, (?:caput, )?([^*]+)\*\*', r'\1 –', t)
    t = re.sub(r'\[\[[^\]|]*\\?\|([^\]]*)\]\]', r'\1', t)
    t = re.sub(r'\[\[([^\]]*)\]\]', r'\1', t)
    t = re.sub(r'\s*\{#[\w-]+\}', '', t)
    t = re.sub(r'(?<![\w/&])#[a-z0-9][a-z0-9-]+', '', t)
    t = re.sub(r'\*\*|__|^#{1,6}\s*', '', t, flags=re.M)
    t = re.sub(r'[ \t]+', ' ', t)
    return re.sub(r'\n{2,}', '\n', t).strip()


def gerar_indice():
    docs, blocos = consultar.carregar(RAIZ)
    sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=RAIZ,
                         capture_output=True, text=True).stdout.strip()
    D = {}
    # normas-mãe primeiro, para os anexos herdarem tipo, esfera e situação
    for n, d in sorted(docs.items(), key=lambda x: 'norma_mae' in x[1]['metadados']):
        m = d['metadados']
        mae = D.get(m.get('norma_mae', '').strip('"[] '), {})
        D[n] = {'t': m.get('norma', '').strip('"') or m.get('titulo', '').strip('"') or n,
                'f': d['arquivo'],
                'tp': m.get('tipo', '') or mae.get('tp', ''),
                'e': m.get('esfera', '') or mae.get('e', ''),
                's': m.get('situacao', '') or mae.get('s', ''),
                'em': m.get('ementa', '').strip('"')[:300],
                'm': m.get('norma_mae', '').strip('"[] ')}
    B = []
    for b in blocos:
        i0 = b['ids'][0] if b['ids'] else ''
        txt = PREFIXO_ANEXO.sub('', limpar(b['texto'])).strip()
        if len(txt) < 3:
            continue
        ctx = ' › '.join(limpar(x) for x in b['contexto'][-2:])[:160]
        tags = sorted(set(TAG.findall(b['texto'])) - {i0.split('_')[0]})
        if '_tab' in i0 or (re.search(r'_lin\d', i0) and ' | ' in txt):
            k = 2  # linha de tabela ou lista
        elif re.search(r'_lin\d', i0):
            k = 1  # trecho de anexo (termo de referência etc.)
        else:
            k = 0  # artigo ou dispositivo
        ant = B[-1] if B else None
        if (k == 1 and ant and ant[7] == 1 and ant[0] == b['norma'] and ant[4] == ctx
                and len(ant[6]) + len(txt) < 1800):
            ant[2] = b['linha_fim']
            ant[6] += '\n' + txt
            ant[5] = sorted(set(ant[5]) | set(tags))
            continue
        B.append([b['norma'], b['linha'], b['linha_fim'], i0, ctx, tags, txt[:4000], k])
    return {'formato': formato_indice(), 'commit': sha, 'docs': D, 'blocos': B}


def ler_motor():
    return (RAIZ / 'site' / 'motor.js').read_text(encoding='utf-8')


def formato_indice():
    return int(FORMATO_INDICE.search(ler_motor())[1])


def main():
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / '_site').resolve()
    if saida.exists():
        shutil.rmtree(saida)
    saida.mkdir(parents=True)
    indice = gerar_indice()

    ambitos = json.loads((RAIZ / 'consultas/ambitos.json').read_text(encoding='utf-8'))
    desconhecidas = [n for n in ambitos['ambitos'] if n not in indice['docs']]
    if desconhecidas:
        # norma ainda não convertida: não quebra o site, só avisa
        print('aviso: ambitos.json cita normas fora da base:', ', '.join(desconhecidas))

    (saida / 'index.json').write_text(
        json.dumps(indice, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    for f in ('index.html', 'motor.js', 'cnae.json', 'assistente.html', 'assistente.js', 'assistente.css', 'estilo.css', 'classificacao.html', 'classificacao.js', 'complementar.js'):
        shutil.copy(RAIZ / 'site' / f, saida / f)
    for f in ('sinonimos.json', 'ambitos.json', 'ctresb-index.json'):
        shutil.copy(RAIZ / 'consultas' / f, saida / f)
    # A curadoria pode ganhar uma norma após a sincronização complementar.
    extra = json.loads((saida / 'ctresb-index.json').read_text(encoding='utf-8'))
    extra['documentos'] = [d for d in extra['documentos'] if d['id'] not in indice['docs']]
    (saida / 'ctresb-index.json').write_text(json.dumps(extra, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    # Índices para recuperação e expansão do grafo na camada de IA.
    # Independentes do index.json, preservam a compatibilidade do motor atual.
    dispositivos, grafo = gerar_grafo.salvar(saida, RAIZ, indice['commit'])
    # Metadados funcionais separados do texto legal; revisão por ID exato.
    (saida / 'classificacao.json').write_text(json.dumps(
        relatorio(dispositivos['dispositivos'], indice['commit']),
        ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    por_norma = collections.defaultdict(list)
    for d in dispositivos['dispositivos']:
        if 'funcao' in d:
            por_norma[d['norma']].append(d)
    for b in indice['blocos']:
        ds = [d for d in por_norma[b[0]] if b[1] <= d['linha_inicio'] <= b[2]]
        categorias = list(dict.fromkeys(c for d in ds for c in d['funcao']['categorias']))
        b.append({'categorias': categorias, 'estado': 'revisada' if ds and
                  all(d['funcao']['estado'] == 'revisada' for d in ds) else 'sugerida'})
    (saida / 'index.json').write_text(json.dumps(indice, ensure_ascii=False,
        separators=(',', ':')), encoding='utf-8')
    # Fatias por norma: o Worker baixa só as das normas selecionadas pelo motor,
    # porque dispositivos.json e grafo.json inteiros estouram a memória dele.
    (saida / 'fatias').mkdir()
    nomes_fatias = []
    for nome, fatia in gerar_grafo.fatias(dispositivos, grafo).items():
        nomes_fatias.append(f'fatias/{nome}.json')
        (saida / nomes_fatias[-1]).write_text(
            json.dumps(fatia, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    # resumo da publicação: clientes conferem o commit e a versão do motor sem baixar o índice
    arquivos = {f: hashlib.sha256((saida / f).read_bytes()).hexdigest()
                for f in ('index.json', 'motor.js', 'cnae.json', 'sinonimos.json', 'ambitos.json',
                          'dispositivos.json', 'grafo.json', 'classificacao.json', 'ctresb-index.json', 'complementar.js', *nomes_fatias)}
    (saida / 'manifesto.json').write_text(json.dumps({
        'commit': indice['commit'],
        'gerado_em': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'motor': MOTOR_VERSAO.search(ler_motor())[1],
        'formato_indice': indice['formato'],
        'arquivos': arquivos,
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    (saida / '.nojekyll').write_text('')

    tipos = collections.Counter(b[7] for b in indice['blocos'])
    print(f"{len(indice['docs'])} arquivos, {len(indice['blocos'])} trechos "
          f"(dispositivos {tipos[0]}, trechos de anexo {tipos[1]}, linhas de lista {tipos[2]}) "
          f"· commit {indice['commit'][:7]} → {saida}")


if __name__ == '__main__':
    main()
