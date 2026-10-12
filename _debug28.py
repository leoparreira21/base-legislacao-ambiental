exec(open('_build28.py',encoding='utf-8').read().split('# output in source order')[0])
for i,b in enumerate(rest):
 if b.startswith('Art. 12') or b.startswith('Art. 13'):
  print(i,repr(b)); print('NEXT',repr(rest[i+1]));
