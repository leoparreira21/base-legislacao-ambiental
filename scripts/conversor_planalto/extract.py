"""Extrai parágrafos de impressões do Planalto (Skia/PDF) com marcação de tachado.
Uso: python extract.py arquivo.pdf saida.json
Cada parágrafo: {"p": página, "x": recuo, "t": texto, "s": fração tachada, "st": texto com ~~ nas palavras tachadas}
"""
import sys, json, re, statistics
import pymupdf

def segs_of(page):
    out = []
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if abs(a.y - b.y) < 0.6 and abs(a.x - b.x) > 2:
                    out.append((min(a.x, b.x), max(a.x, b.x), (a.y + b.y) / 2))
            elif it[0] == 're':
                r = it[1]
                if r.height < 2 and r.width > 2:
                    out.append((r.x0, r.x1, (r.y0 + r.y1) / 2))
    return out

def struck(w, segs):
    x0, y0, x1, y1 = w[:4]
    h = y1 - y0
    cx = (x0 + x1) / 2
    for a, b, y in segs:
        if a <= cx <= b and y0 + 0.30 * h <= y <= y0 + 0.72 * h:
            # exige cobertura de boa parte da palavra
            cov = min(b, x1) - max(a, x0)
            if cov >= 0.6 * (x1 - x0):
                return True
    return False

def lines_of(doc):
    L = []
    for pn, page in enumerate(doc):
        segs = segs_of(page)
        ws = [w for w in page.get_text('words') if not re.fullmatch(r'[\uf000-\uf8ff]+', w[4]) and w[3] > 32]
        hs = sorted(w[3] - w[1] for w in ws) or [10]
        hmed = hs[len(hs) // 2]
        rows = []   # [y0, y1, words]
        for w in sorted(ws, key=lambda w: -(w[3] - w[1])):
            h = w[3] - w[1]
            small = h < 0.8 * hmed or (h < 0.92 * hmed and re.fullmatch(r'[oaº°ª]s?', w[4]) is not None)
            cy = (w[1] + w[3]) / 2
            row = None
            for rw in rows:
                if small:
                    if rw[0] - 1 <= cy <= rw[1] + 1: row = rw; break
                elif abs(rw[1] - w[3]) < 3: row = rw; break
            if row is None:
                row = [w[1], w[3], []]; rows.append(row)
            row[2].append(w)
        rows.sort(key=lambda rw: rw[1])
        for rw in rows:
            r = sorted(rw[2], key=lambda w: w[0])
            toks = []
            prev = None
            for w in r:
                s = struck(w, segs)
                gap = (w[0] - prev[2]) if prev else 0
                hh = w[3] - w[1]
                small = hh < 0.8 * hmed or (hh < 0.92 * hmed and re.fullmatch(r'[oaº°ª]s?', w[4]) is not None)
                if toks and small and gap < 4 and re.search(r'[0-9nN]$', toks[-1][0]) and re.fullmatch(r'[oaº°ª]s?', w[4]) and abs(w[3] - prev[3]) > 1:
                    t0, s0, g0 = toks[-1]
                    toks[-1] = (t0 + w[4], s0, g0)
                else:
                    toks.append((w[4], s, gap))
                prev = w
            L.append({'p': pn + 1, 'y0': min(w[1] for w in r), 'y1': max(w[3] for w in r),
                      'x0': r[0][0], 'x1': r[-1][2], 'toks': toks})
    return L

def fix_ordinals(toks):
    # sublinhado do ordinal ("1o", "no") lido como tachado: desfaz se os vizinhos não estão tachados
    out = list(toks)
    for i, (t, s, g) in enumerate(out):
        if s and re.match(r'^(\d+[oº°ª]|[Nn][oº]s?|§)[,.;:]?$', t):
            l = out[i - 1][1] if i > 0 else False
            r = out[i + 1][1] if i + 1 < len(out) else False
            if not (l or r):
                out[i] = (t, False, g)
    return out

def main(pdf, outp):
    doc = pymupdf.open(pdf)
    L = lines_of(doc)
    # passo entre linhas
    gaps = [b['y0'] - a['y1'] for a, b in zip(L, L[1:]) if a['p'] == b['p']]
    import collections as _c
    marg = {}
    for ln in L:
        marg.setdefault(ln['p'], []).append(ln['x0'])
    marg = {p: sorted(v)[max(0, len(v) // 20)] for p, v in marg.items()}
    paras = []
    cur = None
    for i, ln in enumerate(L):
        new = True
        if cur is not None:
            prev = L[i - 1]
            if prev['p'] == ln['p']:
                new = (ln['y0'] - prev['y1']) > 4.0
                if new and ln['x0'] <= marg[ln['p']] + 3 and re.match(r'^[a-zà-ú0-9(,;.]', ln['toks'][0][0]) \
                        and not re.match(r'^([a-z]\)|\d+\s*[-.)])', ln['toks'][0][0]) and not re.search(r'[.;:]$', prev['toks'][-1][0]):
                    new = False
            else:
                # quebra de página: continuação se a linha anterior não fecha frase
                new = None
        txt_toks = fix_ordinals(ln['toks'])
        if new is None:
            last = cur['toks'][-1][0] if cur['toks'] else ''
            first = ' '.join(x[0] for x in txt_toks[:2])
            cont = not re.search(r'[.;:]\)?$|\)$', last) and not re.match(r'^(Art\.|§|Parágrafo|[IVXLC]+\s*[-–]|[a-z]\)|CAP[IÍ]TULO|T[IÍ]TULO|Seção|LIVRO|PARTE)', first)
            new = not cont
            if not new:
                cur['brk'] = True
        if new:
            if cur: paras.append(cur)
            cur = {'p': ln['p'], 'x': round(ln['x0'], 1), 'toks': []}

        if cur['toks'] and re.search(r'[A-Za-zÀ-ú]-$', cur['toks'][-1][0]) and txt_toks:
            w, s, g = cur['toks'][-1]
            cur['toks'][-1] = (w + txt_toks[0][0], s and txt_toks[0][1], g)
            cur.setdefault('hif', []).append(w + txt_toks[0][0])
            txt_toks = txt_toks[1:]
        cur['toks'].extend(txt_toks)
    if cur: paras.append(cur)
    res = []
    for pa in paras:
        t = ' '.join(x[0] for x in pa['toks'])
        n = len(pa['toks'])
        ns = sum(1 for x in pa['toks'] if x[1])
        st = []
        for w, s, g in pa['toks']:
            st.append(('~' if s else '') + w)
        res.append({'p': pa['p'], 'x': pa['x'], 't': t, 's': round(ns / n, 2) if n else 0,
                    'st': ' '.join(st), 'brk': pa.get('brk', False), 'hif': pa.get('hif', [])})
    json.dump(res, open(outp, 'w'), ensure_ascii=False, indent=0)
    print(len(res), 'parágrafos;', sum(1 for r in res if r['s'] > 0.5), 'tachados;',
          sum(1 for r in res if 0.05 < r['s'] <= 0.5), 'parciais')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
