import pymupdf,re
p=pymupdf.open(r'C:\Users\leo_p\Downloads\acrescentar à base legislação ambiental\IN 28 2026.pdf')
for i in list(range(69,74))+list(range(83,89))+list(range(95,113)):
 t=p[i].get_text(); print(f'\n----- PDF PAGE {i+1} -----\n'+t[:2400])
