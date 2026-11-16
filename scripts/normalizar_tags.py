"""Confere tags candidatas de uma norma nova contra a lista geral e o histórico de decisões.

Uso:
  python scripts/normalizar_tags.py tag1 tag2 ...
  python scripts/normalizar_tags.py --arquivo candidatas.txt     # uma tag por linha (ou separadas por espaço/vírgula)
  python scripts/normalizar_tags.py --json tag1 tag2 ...        # saída em JSON

Para cada candidata, diz o que fazer:
  manter     já existe na lista geral (frontmatter de alguma norma);
  trocar     foi mesclada antes: use a tag destino (consultas/historico-tags.json ou aliases da taxonomia);
  descartar  foi excluída antes, ou é tag de controle;
  revisar    é nova: mostra as tags existentes mais parecidas, para mesclar nelas se for o mesmo tema.
Termina com a lista proposta (manter + trocar, sem repetir) e as novas a revisar.
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from excluir_tags import CONTROLE, vocabulario  # noqa: E402

FORMATO = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')


def sem_plural(t):
    return '-'.join(p[:-1] if len(p) > 4 and p.endswith('s') else p for p in t.split('-'))


def parecidas(t, geral, n=5):
    alvo = sem_plural(t)
    pontos = []
    pal = set(alvo.split('-'))
    for g in geral:
        gs = sem_plural(g)
        r = difflib.SequenceMatcher(None, alvo, gs).ratio()
        comum = pal & set(gs.split('-'))
        if comum:
            r += 0.15 * len(comum)
        if alvo in gs or gs in alvo:
            r += 0.3
        pontos.append((r, g))
    return [g for r, g in sorted(pontos, reverse=True)[:n] if r >= 0.5]


def classificar(cands):
    hist = json.loads((ROOT / 'consultas/historico-tags.json').read_text(encoding='utf-8'))
    tax = json.loads((ROOT / 'consultas/taxonomia-tags.proposta.json').read_text(encoding='utf-8'))
    mescladas = dict(tax.get('aliases', {}))
    mescladas.update(hist['mescladas'])
    excluidas = set(hist['excluidas'])
    geral = set(vocabulario())
    res = []
    for c in cands:
        t = c.strip().lstrip('#').lower()
        if not t:
            continue
        if not FORMATO.match(t):
            res.append({'tag': t, 'acao': 'revisar', 'motivo': 'formato inválido (minúsculas, sem acento, hífen)', 'parecidas': parecidas(t, geral)})
        elif t in CONTROLE:
            res.append({'tag': t, 'acao': 'descartar', 'motivo': 'tag de controle: não é temática (só entra se o corpo a usar)'})
        elif t in geral:
            res.append({'tag': t, 'acao': 'manter', 'motivo': 'já está na lista geral'})
        elif t in mescladas and mescladas[t] in geral:
            res.append({'tag': t, 'acao': 'trocar', 'destino': mescladas[t], 'motivo': 'mesclada antes'})
        elif t in excluidas:
            res.append({'tag': t, 'acao': 'descartar', 'motivo': 'excluída antes'})
        elif sem_plural(t) in geral:
            res.append({'tag': t, 'acao': 'trocar', 'destino': sem_plural(t), 'motivo': 'singular já existe'})
        else:
            res.append({'tag': t, 'acao': 'revisar', 'motivo': 'tag nova', 'parecidas': parecidas(t, geral)})
    proposta = list(dict.fromkeys(r.get('destino', r['tag']) for r in res if r['acao'] in ('manter', 'trocar')))
    novas = [r for r in res if r['acao'] == 'revisar']
    return res, proposta, novas


def main(args):
    if '--arquivo' in args:
        texto = Path(args[args.index('--arquivo') + 1]).read_text(encoding='utf-8')
        cands = re.split(r'[\s,]+', texto)
    else:
        cands = [a for a in args if not a.startswith('--')]
    if not [c for c in cands if c.strip()]:
        print(__doc__)
        return 1
    res, proposta, novas = classificar(cands)
    if '--json' in args:
        print(json.dumps({'candidatas': res, 'proposta': proposta, 'novas_a_revisar': novas}, ensure_ascii=False, indent=2))
        return 0
    for r in res:
        extra = f" -> #{r['destino']}" if 'destino' in r else ''
        sim = f" (parecidas: {', '.join('#' + p for p in r['parecidas'])})" if r.get('parecidas') else ''
        print(f"{r['acao']:9} #{r['tag']}{extra}  [{r['motivo']}]{sim}")
    print(f"\nProposta ({len(proposta)}): " + ', '.join(proposta))
    print(f"Novas a revisar ({len(novas)}): " + ', '.join(r['tag'] for r in novas))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
