"""Parágrafos do texto atualizado da Câmara (pdftotext -layout): parágrafo começa em linha recuada."""
import sys, re, json

def main(lay, outp):
    lines = open(lay, encoding='utf-8').read().split('\n')
    paras, notas = [], {}
    cur = None
    i = 0
    hif = []
    while i < len(lines):
        ln = lines[i].replace('\f', '')
        if re.fullmatch(r'\d{1,2}', ln.strip()):
            # nota de rodapé: até a linha que fecha o parêntese
            n = ln.strip(); txt = []
            i += 1
            while i < len(lines):
                l2 = lines[i].replace('\f', '').strip()
                txt.append(l2)
                i += 1
                if l2.endswith(')'):
                    break
            notas[n] = ' '.join(txt)
            continue
        if not ln.strip():
            i += 1; continue
        ind = len(ln) - len(ln.lstrip(' '))
        s = ln.strip()
        if ind >= 8 or cur is None:
            if cur: paras.append(cur)
            cur = s
        else:
            if re.search(r'[A-Za-zÀ-ú]-$', cur) and re.match(r'^[a-zà-ú]', s):
                hif.append(cur.split()[-1] + s.split()[0])
                cur = cur + s
            else:
                cur = cur + ' ' + s
        i += 1
    if cur: paras.append(cur)
    res = [{'p': 0, 'x': 0, 't': t, 's': 0, 'st': t, 'brk': False, 'hif': []} for t in paras]
    json.dump(res, open(outp, 'w'), ensure_ascii=False, indent=0)
    json.dump({'notas': notas, 'hifens': hif}, open(outp.replace('.json', '.notas.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(res), 'parágrafos;', len(notas), 'notas;', len(hif), 'hifens de fim de linha unidos')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
