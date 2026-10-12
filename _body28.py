import pymupdf
p=pymupdf.open(r'C:\Users\leo_p\Downloads\acrescentar à base legislação ambiental\IN 28 2026.pdf')
for i in [1,4,5,7,8,9,10,11,12,13,14,19,20,24,25,26,27,36,37,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70]:
 t=p[i].get_text(); print(f'\n---PAGE {i+1}---\n{t[:2500]}')
