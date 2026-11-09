"""Confere as palavras do PDF (sem tachados) com as do Markdown gerado.
Uso: CONV_TRAB=<pasta> python verify.py cfg_cf"""
import sys, re, json, collections, importlib
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make

def words(s):
    s = s.replace('º', 'o').replace('°', 'o').replace('ª', 'a')
    return re.findall(r'[0-9A-Za-zÀ-ÿ]+', s)

def md_text(md):
    body = md.split('\n---\n', 1)[1]
    body = body.split('## Relação com outras normas')[0]
    out = []
    for ln in body.splitlines():
        if ln.startswith('# ') or ln.startswith('Tags:') or ln.startswith('Alterações:') or ln.startswith('> Anota'):
            continue
        ln = re.sub(r'^#{2,6} ', '', ln)
        ln = re.sub(r'^\s*- ', '', ln)
        ln = re.sub(r'\*\*[^*]+\*\*', '', ln)
        ln = re.sub(r'\{#[\w-]+\}', '', ln)
        ln = re.sub(r'\[\[[^|\]]*\|([^\]]*)\]\]', r'\1', ln)
        ln = re.sub(r'\[\[([^\]]*)\]\]', r'\1', ln)
        ln = re.sub(r'(?<![\w/&])#[a-z][\w-]*', '', ln)
        out.append(ln)
    return '\n'.join(out)

def main(modname):
    mod = importlib.import_module(modname)
    cfg = mod.cfg
    P, drop = make.paragraphs(cfg)
    texts = [r['t'].strip() for r in P]
    ini = next(i for i, t in enumerate(texts) if re.match(cfg['preambulo_re'], t))
    exc = cfg.get('excluir', lambda t: set())(texts)
    pdf = ' '.join(t for i, t in enumerate(texts[ini:], ini) if i not in exc)
    pdf = re.sub(r'Este texto não substitui o publicado[^\n]*?\d{2,4}\s*\.?', ' ', pdf)
    for x in cfg.get('_excluidos', []):
        pdf = pdf.replace(x, ' ', 1)
    pdf = pdf.replace(' * ', ' ')
    md = open(f"{make.REPO}/normas/{cfg['arquivo']}.md", encoding='utf-8').read()
    a = collections.Counter(words(pdf))
    b = collections.Counter(words(md_text(md)))
    falta = a - b
    sobra = b - a
    print('PDF', sum(a.values()), 'MD', sum(b.values()))
    lab = re.compile(r'^([IVXLC]+|\d+o|[a-z]|Parágrafo|único|Art|Arts|\d{1,3})$')
    falta = collections.Counter({k: v for k, v in falta.items() if not lab.match(k)})
    print('faltam no MD:', sorted(falta.items(), key=lambda x: -x[1])[:60])
    print('sobram no MD:', sorted(sobra.items(), key=lambda x: -x[1])[:60])

if __name__ == '__main__':
    main(sys.argv[1])
