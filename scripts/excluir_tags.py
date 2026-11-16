"""Exclui ou mescla tags temáticas em toda a base.

Uso:
  python scripts/excluir_tags.py tag1 tag2 ...            # simulação: mostra o que mudaria
  python scripts/excluir_tags.py --aplicar tag1 tag2 ...  # grava
  python scripts/excluir_tags.py --mesclar DESTINO ORIGEM1 ORIGEM2 ...            # simulação da mescla
  python scripts/excluir_tags.py --aplicar --mesclar DESTINO ORIGEM1 ORIGEM2 ...  # ORIGENs viram DESTINO
  python scripts/excluir_tags.py --dados                  # regrava docs/tags-editaveis.json (lista da página de exclusão)
  python scripts/excluir_tags.py --pagina SAIDA.html      # monta a página interativa de exclusão com os dados atuais

Onde a tag é apagada:
  - campo `tags` do frontmatter de normas/, normas/anexos/ e normas/comentarios/;
  - qualquer `#tag` que tenha sobrado no corpo desses arquivos;
  - consultas/taxonomia-tags.proposta.json (o nó sai; os filhos passam ao pai dele; aliases para a tag saem);
  - tags.md (regerado pelo validar.py --tags);
  e registra a decisão em consultas/historico-tags.json.
Depois rode `python scripts/validar.py` e `python scripts/gerar_html.py` (html/ e catálogo).
Mesclar: cada ORIGEM é trocada por DESTINO no frontmatter (sem repetir) e no corpo; na taxonomia
os nós das origens saem, os filhos passam para DESTINO e as origens viram aliases de DESTINO.
DESTINO pode ser uma das tags, outra tag existente ou um nome novo (herda o nó da primeira origem).
Tags de controle (#revogado, #redacao-alterada, #incluido, #anexo-pendente) não podem ser excluídas.
"""
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLE = {'revogado', 'redacao-alterada', 'incluido', 'anexo-pendente'}
TAXONOMIA = ROOT / 'consultas/taxonomia-tags.proposta.json'
DADOS = ROOT / 'docs/tags-editaveis.json'
MODELO = ROOT / 'scripts/modelos/exclusao-tags.html'
HISTORICO = ROOT / 'consultas/historico-tags.json'


def registrar(excluidas=(), mesclas=None):
    """Guarda a decisão em consultas/historico-tags.json (usado por normalizar_tags.py)."""
    h = json.loads(HISTORICO.read_text(encoding='utf-8'))
    mes = h['mescladas']
    for o, d in (mesclas or {}).items():
        mes[o] = d
    for o in list(mes):  # resolve cadeias: a -> b e b -> c vira a -> c
        vistos = set()
        while mes[o] in mes and mes[o] not in vistos:
            vistos.add(mes[o])
            mes[o] = mes[mes[o]]
    h['mescladas'] = dict(sorted(mes.items()))
    h['excluidas'] = sorted(set(h['excluidas']) | set(excluidas))
    HISTORICO.write_text(json.dumps(h, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
FM_TAGS = re.compile(r'^tags:\s*\[(.*)\]\s*$', re.M)


def arquivos():
    return sorted(Path(p) for p in glob.glob(str(ROOT / 'normas/**/*.md'), recursive=True))


def separar(texto):
    if texto.startswith('---\n'):
        fim = texto.index('\n---\n', 4) + 5
        return texto[:fim], texto[fim:]
    return '', texto


def tags_de(fm):
    m = FM_TAGS.search(fm)
    return [t.strip().strip('"\'') for t in m[1].split(',') if t.strip()] if m else []


def titulo(fm, arq):
    m = re.search(r'^(?:norma|documento):\s*"?(.*?)"?\s*$', fm, re.M)
    if m:
        return m[1]
    a = re.search(r'^anexo:\s*"?(.*?)"?\s*$', fm, re.M)
    return f'{a[1]} – {arq.stem.rsplit("-anexo", 1)[0]}' if a else arq.stem


def vocabulario():
    uso = {}
    for arq in arquivos():
        fm, _ = separar(arq.read_text(encoding='utf-8'))
        for t in tags_de(fm):
            if t not in CONTROLE:
                uso.setdefault(t, []).append(arq.relative_to(ROOT).as_posix())
    return uso


def gerar_dados():
    uso = vocabulario()
    nomes = {}
    for arq in arquivos():
        fm, _ = separar(arq.read_text(encoding='utf-8'))
        nomes[arq.relative_to(ROOT).as_posix()] = titulo(fm, arq)
    # anexo: "ANEXO IV – <nome da norma-mãe>"
    por_stem = {Path(a).stem: n for a, n in nomes.items()}
    for a, n in nomes.items():
        if ' – ' in n and a.startswith('normas/anexos/'):
            rot, mae = n.split(' – ', 1)
            nomes[a] = f'{por_stem.get(mae, mae)}, {rot}'
    grupo = {n['id']: n.get('grupo') for n in json.loads(TAXONOMIA.read_text(encoding='utf-8'))['nos']}
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    docs = sorted({a for arqs in uso.values() for a in arqs})
    idx = {a: i for i, a in enumerate(docs)}
    dados = {
        'commit': commit,
        'docs': [[a, nomes[a]] for a in docs],
        'tags': [{'tag': t, 'grupo': grupo.get(t) or '', 'd': sorted(idx[a] for a in arqs)}
                 for t, arqs in sorted(uso.items())],
    }
    DADOS.write_text(json.dumps(dados, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'{len(dados["tags"])} tags editáveis em {DADOS.relative_to(ROOT)}')


def excluir(alvo, aplicar):
    mudados = 0
    tag_corpo = re.compile(r'[ \t]*(?<![\w/&{\[|#`])#(' + '|'.join(map(re.escape, sorted(alvo))) + r')(?![\w-])')
    for arq in arquivos():
        orig = arq.read_text(encoding='utf-8')
        fm, corpo = separar(orig)
        atuais = tags_de(fm)
        if any(t in alvo for t in atuais):
            fm = FM_TAGS.sub(lambda m: 'tags: [' + ', '.join(t for t in atuais if t not in alvo) + ']', fm, count=1)
        corpo = tag_corpo.sub('', corpo)
        novo = fm + corpo
        if novo != orig:
            mudados += 1
            if aplicar:
                arq.write_text(novo, encoding='utf-8')
    tax = json.loads(TAXONOMIA.read_text(encoding='utf-8'))
    pai_de = {n['id']: n.get('pai') for n in tax['nos']}

    def subir(p):
        while p in alvo:
            p = pai_de.get(p)
        return p

    nos = []
    for n in tax['nos']:
        if n['id'] in alvo:
            continue
        if n.get('pai') in alvo:
            n['pai'] = subir(n['pai'])
        nos.append(n)
    removidos_tax = len(tax['nos']) - len(nos)
    tax['nos'] = nos
    tax['aliases'] = {a: t for a, t in tax['aliases'].items() if a not in alvo and t not in alvo}
    if aplicar:
        TAXONOMIA.write_text(json.dumps(tax, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        subprocess.run([sys.executable, 'scripts/validar.py', '--tags'], cwd=ROOT, check=True, capture_output=True)
        registrar(excluidas=alvo)
    acao = 'excluídas' if aplicar else 'seriam excluídas (simulação; use --aplicar)'
    print(f'{len(alvo)} tag(s) {acao}: {mudados} arquivo(s) de normas, {removidos_tax} nó(s) da taxonomia.')


FORMATO = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')


def mesclar(destino, origens, aplicar):
    mudados = 0
    corpo_re = re.compile(r'(?<![\w/&{\[|#`])#(' + '|'.join(map(re.escape, sorted(origens))) + r')(?![\w-])')
    for arq in arquivos():
        orig = arq.read_text(encoding='utf-8')
        fm, corpo = separar(orig)
        atuais = tags_de(fm)
        if any(t in origens for t in atuais):
            novas = list(dict.fromkeys(destino if t in origens else t for t in atuais))
            fm = FM_TAGS.sub(lambda m: 'tags: [' + ', '.join(novas) + ']', fm, count=1)
        corpo = corpo_re.sub('#' + destino, corpo)
        novo = fm + corpo
        if novo != orig:
            mudados += 1
            if aplicar:
                arq.write_text(novo, encoding='utf-8')
    tax = json.loads(TAXONOMIA.read_text(encoding='utf-8'))
    nos = {n['id']: n for n in tax['nos']}
    if destino not in nos:
        base = next((nos[o] for o in sorted(origens) if o in nos), None)
        if base:
            base = dict(base, id=destino)
            tax['nos'].append(base)
            nos[destino] = base
    pai_de = {i: n.get('pai') for i, n in nos.items()}

    def subir(p):
        while p in origens or p == destino:
            p = pai_de.get(p) if p != destino else None
        return p

    lista = []
    for n in tax['nos']:
        if n['id'] in origens:
            continue
        if n['id'] == destino:
            if n.get('pai') in origens or n.get('pai') == destino:
                n['pai'] = subir(n['pai'])
        elif n.get('pai') in origens:
            n['pai'] = destino
        lista.append(n)
    tax['nos'] = sorted(lista, key=lambda n: n['id'])
    aliases = {a: (destino if t in origens else t) for a, t in tax['aliases'].items() if a != destino}
    aliases.update({o: destino for o in origens})
    tax['aliases'] = aliases
    if aplicar:
        TAXONOMIA.write_text(json.dumps(tax, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        subprocess.run([sys.executable, 'scripts/validar.py', '--tags'], cwd=ROOT, check=True, capture_output=True)
        registrar(mesclas={o: destino for o in origens})
    acao = 'mescladas' if aplicar else 'seriam mescladas (simulação; use --aplicar)'
    print(f'{len(origens)} tag(s) {acao} em #{destino}: {mudados} arquivo(s) de normas.')


def main(args):
    if '--dados' in args:
        gerar_dados()
        return 0
    if '--pagina' in args:
        gerar_dados()
        saida = Path(args[args.index('--pagina') + 1])
        dados = DADOS.read_text(encoding='utf-8').strip().replace('</', '<\\/')
        saida.write_text(MODELO.read_text(encoding='utf-8').replace('/*DADOS*/null', dados), encoding='utf-8')
        print(f'página em {saida}')
        return 0
    aplicar = '--aplicar' in args
    if '--mesclar' in args:
        nomes = [a.strip().lstrip('#').strip(',') for a in args if not a.startswith('--')]
        nomes = [a for a in nomes if a]
        if len(nomes) < 2:
            print('Use: --mesclar DESTINO ORIGEM1 [ORIGEM2 ...]')
            return 1
        destino, origens = nomes[0], set(nomes[1:]) - {nomes[0]}
        if not FORMATO.match(destino):
            print(f'Nome inválido para o destino: {destino} (minúsculas, sem acento, hífen entre palavras)')
            return 1
        if not origens:
            print('Informe ao menos uma tag diferente do destino.')
            return 1
        if (origens | {destino}) & CONTROLE:
            print(f'Tags de controle não podem ser mescladas: {sorted((origens | {destino}) & CONTROLE)}')
            return 1
        desconhecidas = origens - set(vocabulario())
        if desconhecidas:
            print(f'Tags que não existem na base: {sorted(desconhecidas)}')
            return 1
        mesclar(destino, origens, aplicar)
        if aplicar:
            gerar_dados()
        return 0
    alvo = {a.strip().lstrip('#').strip(',') for a in args if not a.startswith('--')} - {''}
    if not alvo:
        print(__doc__)
        return 1
    proibidas = alvo & CONTROLE
    if proibidas:
        print(f'Tags de controle não podem ser excluídas: {sorted(proibidas)}')
        return 1
    desconhecidas = alvo - set(vocabulario())
    if desconhecidas:
        print(f'Tags que não existem na base: {sorted(desconhecidas)}')
        return 1
    excluir(alvo, aplicar)
    if aplicar:
        gerar_dados()
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
