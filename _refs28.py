import pymupdf,re
p=pymupdf.open(r'C:\Users\leo_p\Downloads\acrescentar à base legislação ambiental\IN 28 2026.pdf')
t='\n'.join(x.get_text() for x in p[:71])
for pat in [r'(?i)Lei (?:Federal |Estadual )?(?:n\.?º\s*)?[\d.]+/\d{4}',r'(?i)Decreto (?:Federal |Estadual )?(?:n\.?º\s*)?[\d.]+/\d{4}',r'(?i)Resolu[cç][aã]o (?:CONAMA|CEMA|SEDEST) (?:n\.?º\s*)?[\d.]+/\d{4}',r'(?i)Portaria [A-Z/ ]+n\.?º?\s*[\d.]+/\d{4}',r'(?i)Instru[cç][aã]o Normativa (?:IBAMA )?(?:n\.?º\s*)?[\d.]+/\d{4}']:
 print('\n',sorted(set(re.findall(pat,t))))
