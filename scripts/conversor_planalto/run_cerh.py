import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from gen_cerh import build
PEND = '#anexo-pendente'
def blocos(titulo_intro, partes):
    o=['## ANEXOS','','### ANEXO {#anexo1}','',titulo_intro,'']
    for i,(rot,desc) in enumerate(partes,1):
        o.append(f'- **Anexo, parte {i}** {{#anexo1_lin{i}}} {PEND} {rot}: {desc}')
    return o+['']
# CERH 42
p42=[('Deliberação nº 05/2020 do CBH Paraná 3 (PDF, págs. 4 a 7)','aprova os critérios de enquadramento, a atualização do enquadramento e o Programa para Efetivação do Enquadramento; conteúdo normativo (tipo 3), não transcrito'),
 ('Anexo I da Deliberação nº 05/2020 (PDF, págs. 8 a 45)','tabela de trechos de corpos de água com AEG, descrição, classe por horizonte (curto, médio e longo prazo e meta final), fuso e comprimento; conteúdo normativo (tipo 3), não transcrito'),
 ('Mapas das metas de curto, médio e longo prazo e meta final (PDF, págs. 46 a 53)','figuras cartográficas, não transcritas'),
 ('Deliberação nº 06/2022 do CBH Paraná 3 (PDF, págs. 54 e 55)','muda os critérios de curto e médio prazo do Rio das Antas – 01; não transcrita'),
 ('Parecer Técnico nº 01/2025 – CTPLAN – CBH Paraná 3 (PDF, págs. 56 a 68)','pareceres sobre reenquadramento de trechos, com tabelas; não transcrito'),
 ('Deliberação nº 18/2025 e Ofício nº 01/2025 do CBH Paraná 3 (PDF, págs. 69 a 71)','encaminhamento ao CERH; não transcritos')]
build('42','ESPECIAL_resolu__o_CERH_42_2026.txt',
 'Aprova o enquadramento dos corpos de água superficiais na área de abrangência do Comitê da Bacia do Paraná 3, em classes, de acordo com os usos preponderantes.','',None,None,
 [('1','Aprovar os critérios de enquadramento, a proposta de atualização do enquadramento dos corpos de água da bacia hidrográfica do Paraná 3, bem como o reenquadramento dos corpos d’água superficiais na área de abrangência do Comitê da Bacia Hidrográfica do Rio Paraná 3, conforme anexo a esta resolução.'),
  ('2','Esta Resolução entra em vigor na data de publicação.')],
 blocos('A resolução (art. 1º) aprova o reenquadramento “conforme anexo a esta resolução”, sem numerar nem nomear o anexo. O PDF enviado reúne, depois da assinatura, os documentos abaixo, que não foram transcritos (ver Notas de transcrição).',p42),
 ['- Aprova o enquadramento e o reenquadramento dos corpos de água da Bacia do Paraná 3; as classes por trecho estão no anexo (pendente), de modo que a resolução, sozinha, não permite saber a classe de um trecho.',
  '- Cita a [[lei-estadual-12726-1999]] e o [[decreto-estadual-9129-2010]] (competência do CERH). Referência ao Decreto nº 9.130/2010 consta apenas nos documentos anexados.',
  '- Complementa a [[resolucao-cerh-43-2026]], aprovada na mesma data, que trata de condicionante e do Termo de Reenquadramento.'],
 ['Fonte: PDF da edição especial do Diário Oficial do Estado enviado por Leo (71 páginas); a resolução ocupa as págs. 1 a 3 e o restante são documentos do processo anexados, com marca do e-protocolo (protocolo 24.813.216-7).',
  '- Removidos: rodapés de assinatura avançada do e-protocolo, numerações de folha e marcas d’água.',
  '- Anexos não transcritos (`#anexo-pendente`): a tabela de trechos (págs. 8 a 45, cerca de 300 linhas com coordenadas) tem a camada de texto do PDF corrompida (espaços e vírgulas perdidos nos números), então só pode ser lida das imagens; a transcrição fica para decisão de Leo.',
  '- A norma não informa o número nem a data do Diário Oficial; `data_publicacao` repete a data de assinatura (14/04/2026) e deve ser conferida.',
  '- O art. 1º usa “Comitê da Bacia Hidrográfica do Rio Paraná 3” (com “Rio”), enquanto os considerandos usam “Comitê da Bacia do Paraná 3”; mantido como publicado.'],{})
# CERH 43
p43=[('Deliberação nº 14/2025 do CBH Paraná 3 (PDF, pág. 4)','aprova o Termo de Referência de Reenquadramento; não transcrita'),
 ('Termo de Referência – Estudo para Reenquadramento de Trechos de Corpos Hídricos da Área de Abrangência do CBH Paraná 3 (PDF, págs. 5 a 16)','diretriz de estudo (tipo 2), com seu Anexo I (conteúdo mínimo do estudo) e Anexo II (fluxograma); não transcrito'),
 ('Parecer Técnico nº 01/2025 – CTPLAN – CBH Paraná 3 (PDF, págs. 17 a 29)','recomendações de reenquadramento de trechos, com tabelas de classe por horizonte; conteúdo normativo (tipo 3), não transcrito'),
 ('Deliberação nº 18/2025 e Ofício nº 01/2025 do CBH Paraná 3 (PDF, págs. 30 a 32)','aprovação das recomendações, com exceção dos itens 6 e 8, e encaminhamento ao CERH; não transcritos')]
build('43','ESPECIAL_resolu__o_CERH_43_2026.txt',
 'Aprova o reenquadramento dos corpos de água superficiais na área de abrangência do Comitê da Bacia Hidrográfica do Paraná 3, em classes, de acordo com os usos preponderantes.','',None,None,
 [('1','Estabelecer a condicionante de que o Comitê da Bacia Hidrográfica do Paraná 3 deve, em uma de suas próximas reuniões ordinárias ou extraordinárias, apresentar em plenária o histórico e procedimentos realizados pelo comitê e suas câmaras técnicas na discussão do reenquadramento de trechos de corpos hídricos em seu território de abrangência, conforme apresentado na 43ª Reunião Ordinária do CERH, realizada em 20 de março de 2026.'),
  ('2','Aprovar o Termo de Reenquadramento, assim como as alterações aprovadas pela plenária do Comitê da Bacia Hidrográfica do Paraná 3 apresentadas na 43ª Reunião Ordinária do CERH, realizada em 20 de março de 2026.'),
  ('3','Esta Resolução entra em vigor na data de publicação.')],
 blocos('A resolução (art. 2º) aprova o “Termo de Reenquadramento”, sem numerar anexos. O PDF enviado reúne, depois da assinatura, os documentos abaixo, que não foram transcritos (ver Notas de transcrição).',p43),
 ['- Complementa a [[resolucao-cerh-42-2026]], aprovada na mesma data.',
  '- O art. 2º aprova o “Termo de Reenquadramento”, que o PDF não identifica com esse título; entende-se que seja o conjunto de documentos anexados (Parecer Técnico nº 01/2025 e Termo de Referência), a conferir pelo usuário.',
  '- Cita a [[lei-estadual-12726-1999]] e o [[decreto-estadual-9129-2010]]; a Deliberação nº 18/2025 reencaminha os itens 6 (Bacia Arroio Fundo) e 8 (Bacia do Rio Marreco) à CTINS, e a resolução não os decide.'],
 ['Fonte: PDF da edição especial do Diário Oficial do Estado enviado por Leo (32 páginas); a resolução ocupa as págs. 1 a 3 e o restante são documentos do processo anexados, com marca do e-protocolo (protocolo 24.813.216-7).',
  '- Removidos: rodapés de assinatura avançada do e-protocolo e numerações de folha.',
  '- Anexos não transcritos (`#anexo-pendente`): Termo de Referência (tipo 2, depende do fluxo de subagentes e síntese), Parecer Técnico com tabelas (tipo 3) e deliberações e ofício do comitê; decisão de Leo sobre o que deve entrar na base.',
  '- A norma não informa o número nem a data do Diário Oficial; `data_publicacao` repete a data de assinatura (14/04/2026) e deve ser conferida.',
  '- O nome do signatário aparece como “EVERTON LUIZA DA COSTA SOUZA” nesta resolução (e como “EVERTON LUIZ DA COSTA SOUZA” na Resolução CERH nº 42/2026 e nos rodapés de assinatura); mantido como publicado.'],{'assin':'EVERTON LUIZA DA COSTA SOUZA'})
