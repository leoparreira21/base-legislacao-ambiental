"""Tags por artigo a partir de regras (regex sobre o texto do artigo inteiro).
Uso no cfg: 'tags': tagger.por_regras(REGRAS)  com REGRAS = [(r'regex', '#tag'), ...]
As regras rodam sobre o texto sem acento e em minúsculas.
"""
import re, unicodedata

def _norm(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()

def _texto(n):
    t = n.text + ' ' + ' '.join(c for c, _ in n.extra)
    for k in n.kids:
        t += ' ' + _texto(k)
    return t

def por_regras(regras, max_tags=5, extra=None):
    comp = [(re.compile(rx), tg) for rx, tg in regras]
    def f(pr):
        out = {}
        for it in pr.items:
            if it[0] != 'art':
                continue
            a = it[1]
            t = _norm(_texto(a))
            if not t.strip():
                continue
            tg = []
            for rx, tag in comp:
                if tag not in tg and rx.search(t):
                    tg.append(tag)
            if tg:
                out[a.id] = tg[:max_tags]
        for k, v in (extra or {}).items():
            out[k] = list(dict.fromkeys(out.get(k, []) + v))
        return out
    return f
