import pymupdf,re
p=pymupdf.open(r'C:\Users\leo_p\Downloads\acrescentar à base legislação ambiental\IN 28 2026.pdf')
for i,pg in enumerate(p):
 t=pg.get_text()
 marks=re.findall(r'(?m)^\s*(?:Art\.?\s*\d+[^\n]*|CAP[IÍ]TULO\s+[^\n]*|ANEXO\s+[IVXLCDM]+[^\n]*|Se[cç][aã]o\s+[^\n]*)',t)
 if marks: print(f'P{i+1}: '+' | '.join(marks[:7]))
