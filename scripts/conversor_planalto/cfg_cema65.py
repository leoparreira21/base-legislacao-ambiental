import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from estadual import *

ARQ = 'resolucao-cema-65-2008'

def pre(t):
    t = link_estadual(t, ARQ)
    return t

def L(n, rot, extra=''): 
    return f'- **{rot}** {{#{n}}} {extra}'

G1 = [('01','AÇÚCAR E ALCOOL.'),('02','AGROPECUÁRIA.'),('03','AGROTÓXICOS.'),('04','DESMEMBRAMENTO.'),('05','FLORESTAL.'),('06','TURISMO E LAZER.'),('07','INDÚSTRIA DE MADEIRA.'),('08','BENEFICIAMENTO DE MANDIOCA.'),('09','LINHAS DE TRANSMISSÃO.'),('10','EXTRAÇÃO E TRATAMENTO DE MINEIRAIS.'),('11','TRANSPORTE, TERMINAIS E DEPÓSITOS.'),('12','INDÚSTRIA DE PAPEL E CELULOSE.'),('13','INDÚSTRIA DE COUROS E PELES.'),('14','INDÚSTRIA QUÍMICA.'),('15','INDÚSTRIA DE PRODUTOS ALIMENTARES E BEBIDAS.'),('16','BENEFICIAMENTO DE MINERAIS NÃO METÁLICOS.'),('17','BENEFICIAMENTO DE PRODUTOS AGRÍCOLAS.'),('18','INDÚSTRIA MECÂNICA.'),('19','INDÚSTRIA DE FUMO.'),('20','INDÚSTRIA DE MATERIAL DE TRANSPORTE.'),('21','INDÚSTRIA DE MATERIAL ELÉTRICO, ELETRÔNICO E DE COMUNICAÇÕES.'),('22','EMPREENDIMENTOS COMERCIAIS E DE SERVIÇOS.'),('23','INDÚSTRIAS DIVERSAS.'),('24','USINAS DE GERAÇÃO DE ENERGIA.'),('25','INDÚSTRIA TÊXTIL, DE VESTUÁRIO, CALÇADOS E ARTEFATOS DE TECIDO.'),('26','SANEAMENTO BÁSICO E DRENAGEM.'),('27','INDÚSTRIA DE PRODUTOS DE MATÉRIA PLÁSTICA.'),('28','OBRAS VIÁRIAS'),('29','INDÚSTRIA METALÚRGICA.'),('30','INDÚSTRIA DE BORRACHA.'),('31','EMPREENDIMENTOS IMOBILIÁRIOS.'),('32','DISPOSIÇÃO DE RESÍDUOS SÓLIDOS INDUSTRIAIS, URBANOS E DE SERVIÇOS DE SAÚDE.')]

T1 = [
 ('Licença Ambiental Simplificada - LAS','Todos os Grupos de Atividades Previstos em Resolução','','06 (seis) anos. Renovável'),
 ('Licença Prévia - LP','Todos os Grupos de Atividades','','02 (dois) anos. Não renovável'),
 ('Licença de Instalação - LI','Todos os Grupos de Atividades','','02 (dois) anos. Renovável'),
 ('Licença de Operação - LO','01, 08, 12, 13, 14, 29, 32','De acordo com o Plano de Controle Ambiental','02 (dois) anos. Renovável a critério do IAP.'),
 ('Licença de Operação - LO','10, 11, 15, 16, 18, 20, 21, 23, 25, 30, 03','De acordo com o Plano de Controle Ambiental.','04 (quatro) anos. Renovável a critério do IAP.'),
 ('Licença de Operação - LO','02, 06, 07, 09, 17, 19, 22, 24, 26, 27, 28, 31','De acordo com o Plano de Controle Ambiental.','06 (seis) anos. Renovável a critério do IAP.'),
 ('Declaração de Dispensa de Licenciamento Ambiental Estadual','Todos os Grupos de Atividades Previstos em Resolução','','06 (seis) anos. Renovável a critério do IAP.'),
 ('Autorizações Ambientais','Todas as Modalidades','01 (um) mês','01 (um) ano'),
]
T2 = [
 ('Corte em Manejo de Bracatinga','01 (um) mês','03 (três) anos Renovável'),
 ('Corte em Manejo Rendimento Sustentável','De acordo com o cronograma de execução','02 (dois) anos. Renovável em até 01 (um) ano.'),
 ('Corte Raso','01 (um) mês','01 (um) ano. Renovável em até 06 (seis) meses.'),
 ('Aproveitamento de Material Lenhoso','01 (um) mês','01 (um) ano. Renovável em até 06 (seis) meses.'),
 ('Corte Isolado','01(um) mês','06 (seis) meses. Não renovável.'),
 ('Corte de Vegetação Nativa em Área de Utilidade Pública e/ou Interesse Social.','01 (um) mês','01 (um) ano. Renovável em até 06 (seis) meses.'),
 ('Queima Controlada.','01 (um) mês','06 (seis) meses.'),
 ('Anuência Prévia para Desmembramento, Parcelamento e Unificação de Glebas Rurais.','01 (um) mês','01 (um) ano. Renovável a critério do IAP.'),
]
A5 = [
 ('A análise e apresentação de Estudos Ambientais , conforme conceito desta Resolução, a serem apresentados ao IAP em qualquer fase do licenciamento ambiental ou em outras situações quando exigido pelo IAP, deverão atender os critérios abaixo', []),
 ('1. Os estudos ambientais exigidos pelo IAP, deverão ser apresentados de acordo com as diretrizes específicas para cada empreendimento ou atividade de acordo com as Resoluções (empreendimentos industriais, agropecuários, esgoto sanitário, etc.).', []),
 ('2. Os estudos ambientais deverão ser elaborados por profissionais devidamente habilitados nas áreas a que se referem, conforme estabelecem os conselhos de classe.', []),
 ('3. Antes do encaminhamento dos estudos ambientais para análise técnica da sede, deverá ser verificado pelos Escritórios Regionais os seguintes itens:', [
   '- Se o estudo esta sendo apresentado de acordo com as diretrizes específicas deste IAP;',
   '- A ART do responsável técnico a ser apresentada deve ser específica para o estudo apresentado, na qual deverá ser descrito e detalhado o serviço executado, como por exemplo, na elaboração de projeto de sistema de controle de poluição ambiental, deverá ser especificados tratamento de efluentes líquidos, de resíduos sólidos, de emissões atmosféricas, de controle de ruídos e outros pertinentes;',
   '- Em se tratando de readequação de projeto de unidades já implantadas, encaminhar projeto anterior e um relatório com a situação atual da unidade;',
   '- No caso de apresentação de complementações em atendimento a solicitações do IAP, encaminhar o projeto anterior.']),
 ('4. Os estudos ambientais deverão ser analisados por técnicos deste IAP, devidamente habilitados nas áreas a que se referem os mesmos, conforme estabelecem os conselhos de classe, fazendo parte dessa análise, no mínimo:', [
   '- Atendimento as diretrizes específicas;','- Avaliação da viabilidade técnica da tecnologia proposta;','- Parâmetros básicos de dimensionamento;','- Proposta de monitoramento;','- Emissão de parecer técnico.']),
 ('5. Via do estudo analisado que será mantida no respectivo Escritório Regional deverá ser carimbada pelo técnico responsável pela análise, mesmo quando devolvidos para reapresentação.', []),
 ('6. Os pareceres técnicos serão de conhecimento interno. Quando for necessário repassar informações ao interessado, esta será feita através de ofício encaminhado ao responsável pelo empreendimento ou atividade.', []),
 ('7. Estudos ambientais incompletos e que não atendam às diretrizes específicas, bem como não viáveis tecnicamente, serão devolvidos à empresa. Através de ofício IAP fixará prazo para sua reapresentação. Os processos administrativos dos quais fazem parte os estudos ambientais que não sejam reapresentados no prazo estabelecido serão arquivados e o estudo ambiental considerado como não apresentado. Tal procedimento deverá ser comunicado oficialmente à empresa a qual estará sujeita às penalidades legais.', []),
 ('8. Os estudos ambientais reapresentados, conforme item 7, deverão ser protocolados no IAP para anexação ao processo original, sendo cobrada nova taxa ambiental de análise. Em hipótese alguma reapresentações de estudos ambientais poderão ser entregues ao IAP sem protocolo.', []),
 ('9. Os estudos ambientais poderão ser reapresentados uma vez. Caso não atenda as solicitações de readequações por parte deste IAP, o mesmo será arquivado e considerado como não apresentado. Tal procedimento deverá ser comunicado oficialmente à empresa a qual estará sujeita às penalidades legais.', []),
 ('10. Em se tratando da apresentação de estudos que não estejam vinculados a processos de licenciamento ambiental, como por exemplo, referentes a readequações ou melhorias de sistemas e medidas de controle ambiental implantadas, o interessado deverá solicitar Autorização Ambiental, cujo processo a ser protocolado deverá conter:', [
   'a) Requerimento de Licenciamento Ambiental;','b) Cópia da Licença de Operação ou do Termo de Ajustamento de Conduta Ambiental (TAC);','c) Estudo Ambiental em duas vias e apresentado de acordo com as diretrizes específicas do IAP;','d) Em se tratando de readequação de sistemas de controle ambiental já implantados, encaminhar o estudo anterior e um relatório com a situação atual do sistema justificando o motivo da readequação;','e) Comprovante de recolhimento da Taxa Ambiental (Ficha de Compensação Bancária) de acordo com a IN 100.004.']),
 ('11. No caso de analise de Relatórios de Auditorias Ambientais deverão ser atendidos os critérios estabelecidos na PORTARIA IAP Nº 145, DE 20 DE SETEMBRO DE 2005.', []),
]

def anexos(rd, rest):
    o = ['## ANEXOS', '']
    o += ['### ANEXO I – MODELO DE CERTIDÃO DO MUNICÍPIO QUANTO AO USO E OCUPAÇÃO DO SOLO {#anexo1}', '',
          'Modelo de certidão do Município quanto ao uso e ocupação do solo', '',
          '*(Tipo 1: modelo, conteúdo não transcrito. Exigido em: [[#art4_par1|art. 4º, § 1º]].)*', '']
    o += ['### ANEXO II – TERMO DE AJUSTAMENTO DE CONDUTA {#anexo2}', '',
          'Modelo de Termo de Ajustamento de Conduta', '',
          '*(Tipo 1: modelo, conteúdo não transcrito. Exigido em: [[#art24_cpt|art. 24, caput]], [[#art24_par1|art. 24, § 1º]], [[#art78_cpt|art. 78, caput]] e [[#art78_par1u|art. 78, parágrafo único]].)*', '']
    o += ['### ANEXO III – REQUERIMENTO DE LICENCIAMENTO AMBIENTAL {#anexo3}', '',
          'Modelo de requerimento de licenciamento ambiental – RLA', '',
          '*(Tipo 1: modelo, conteúdo não transcrito. Exigido em: [[#art4_cpt_inc1|art. 4º, caput, inciso I]] e [[#art76_par1_inc1|art. 76, § 1º, inciso I]] (esta remissão diz "Anexo 3").)*', '']
    o += ['### ANEXO IV – VALIDADE DAS LICENÇAS {#anexo4}', '']
    o += ['- **Anexo IV, Tabela 1, título** {#anexo4_tab1_cab} VALIDADE DAS LICENÇAS', '']
    for i,(m,g,mi,ma) in enumerate(T1,1):
        o.append(f'- **Anexo IV, Tabela 1, linha {i}** {{#anexo4_tab1_lin{i}}} Modalidade: {m} | Grupo de atividades: {g} | Prazo mínimo: {mi or "(em branco no original)"} | Prazo máximo: {ma}')
    o += ['', '- **Anexo IV, Tabela 2, título** {#anexo4_tab2_cab} AUTORIZAÇÕES FLORESTAIS', '']
    for i,(m,mi,ma) in enumerate(T2,1):
        o.append(f'- **Anexo IV, Tabela 2, linha {i}** {{#anexo4_tab2_lin{i}}} Modalidade: {m} | Prazo mínimo: {mi} | Prazo máximo: {ma}')
    o += ['', '- **Anexo IV, Tabela 3, título** {#anexo4_tab3_cab} 1.1 IDENTIFICAÇÃO DOS GRUPOS DE ATIVIDADES', '']
    for i,(n,d) in enumerate(G1,1):
        o.append(f'- **Anexo IV, Tabela 3, linha {i}** {{#anexo4_tab3_lin{i}}} Grupo: {n} | Atividade: {d}')
    o += ['', '### ANEXO V – CRITÉRIOS PARA APRESENTAÇÃO E ANÁLISE DE ESTUDOS AMBIENTAIS {#anexo5}', '']
    for i,(t,sub) in enumerate(A5,1):
        o.append(f'- **Anexo V, linha {i}** {{#anexo5_lin{i}}} {rd.links(t, "corpo")}')
        o += ['  ' + x for x in sub]
    o.append('')
    return o

def notas(rd, pr, drop):
    return [
     '- Fonte: impressão de página do portal de legislação estadual em PDF (11 páginas, gerada pelo Chrome/Skia), enviada por Leo, mais cinco PDFs de anexos (Anexos I a V). A publicação oficial foi no Diário Oficial nº 7758, de 08/07/2008; o texto transcrito não substitui o publicado.',
     '- O portal exibe o texto inteiro tachado, porque a norma foi revogada por inteiro pela [[resolucao-cema-105-2019]] (não consta da base). A tachadura é efeito de exibição do portal e não foi reproduzida; o texto foi transcrito como estava, sem marcar dispositivos como `#revogado`.',
     '- Removidos: cabeçalho e rodapé do portal (URL, data e hora de impressão, numeração de páginas) e a lista de nomes de arquivos de anexos do portal (“ANEXOS: Arquivo anexo…”), que não faz parte do texto da norma.',
     '- Dispositivos que o PDF fundiu num único parágrafo (incisos, alíneas e parágrafos corridos na mesma linha, como os incisos I a XIII do art. 1º e os incisos XV e XVI do art. 80) foram separados em linhas próprias, na ordem do original; o texto não foi alterado.',
     '- Grafias do original mantidas, conferidas na imagem do PDF: “bemestar” (art. 1º, definição de poluição), “delimitálas” (art. 2º), “matériasprimas” (art. 76, caput) e “doConselho” (preâmbulo), sem hífen ou espaço; no Anexo IV, “MINEIRAIS” (Tabela 3, linha 10) e “01(um) mês” (Tabela 2, linha 5); no Anexo V, “esta sendo” (item 3) e “analise” (item 11).',
     '- Remissões do próprio texto a conferir: o art. 76, § 1º, inciso I, chama o requerimento de “Anexo 3”, enquanto o art. 4º, inciso I, o chama de “Anexo III”; o art. 75 remete ao art. 8º, parágrafo único, da Resolução CONAMA nº 237/1997.',
     '- Anexos I, II e III: modelos (tipo 1), não transcritos. Anexos IV e V: conteúdo normativo (tipo 3). O Anexo IV foi lido das imagens das páginas: Tabela 1 com 8 linhas (as três linhas da Licença de Operação desfeitas por grupo de atividades), Tabela 2 com 8 linhas e Tabela 3 com 32 grupos; o quadro de grupos do PDF tem uma célula vazia ao final, não transcrita. Anexo V: introdução (linha 1) e itens 1 a 11 (linhas 2 a 12), com os subitens aninhados sob o item.',
     '- Em “Prazo mínimo” de LAS, LP, LI e Declaração de Dispensa o original deixa a célula em branco.',
    ]

cfg = {
    'json': 'c65n', 'arquivo': ARQ,
    'titulo': 'Resolução CEMA nº 65, de 1º de julho de 2008',
    'preambulo_re': r'^O Conselho Estadual', 'preambulo_n': 1,
    'fecho_re': r'^Curitiba',
    'niveis': {'CAPITULO': 2, 'SECAO': 3},
    'ementa_md': 'Dispõe sobre o licenciamento ambiental, estabelece critérios e procedimentos a serem adotados para as atividades poluidoras, degradadoras e/ou modificadoras do meio ambiente e adota outras providências.',
    'pre': pre, 'cita_extra': CITADAS, 'split': split_dispositivos,
    'fm': {
        'norma': 'Resolução CEMA nº 65/2008', 'arquivo': ARQ, 'tipo': 'resolucao', 'esfera': 'estadual',
        'numero': '65', 'ano': '2008', 'data_assinatura': '2008-07-01', 'data_publicacao': '2008-07-08',
        'publicacao': 'Diário Oficial nº 7758, de 08/07/2008',
        'vigencia': 'na data da publicação (art. 82), observadas as disposições aos processos em tramitação',
        'orgao': 'Conselho Estadual do Meio Ambiente – CEMA/PR',
        'ementa': '"Dispõe sobre o licenciamento ambiental, estabelece critérios e procedimentos a serem adotados para as atividades poluidoras, degradadoras e/ou modificadoras do meio ambiente e adota outras providências."',
        'situacao': 'revogada', 'texto': 'original, revogada por inteiro',
        'regulamenta': '[]', 'regulamentado_por': '[]', 'altera': '[]', 'revoga': '[]',
        'revogado_por': '["[[resolucao-cema-105-2019]]"]',
        'fonte': '"Impressão de página da internet em PDF (portal de legislação estadual, 11 páginas), enviada por Leo; o rodapé traz \\"Este texto não substitui o publicado no Diário Oficial do Estado\\""',
    },
    'tags': {},
    'assinaturas': lambda a: [x for x in a if x.strip()],
    'apos_assinatura': anexos,
    'relacao': [
      '- Revogada por inteiro pela [[resolucao-cema-105-2019]] (não consta da base); por isso a norma é mantida como texto original, com `situacao: revogada`.',
      '- O art. 82 revoga, ainda, os arts. 1º a 56 e 76 a 87 da Resolução SEMA nº 31/1998 e a Resolução SEMA nº 18/2004, que não constam da base; nenhuma relação `revoga` foi registrada no frontmatter por falta do arquivo dessas normas.',
      '- Cita normas fora da base (por exemplo, a Resolução CONAMA nº 237/1997); os links ficam pendentes até a inclusão delas.',
    ],
    'notas': notas,
}
if __name__ == '__main__':
    build(cfg)
    n = post_considerandos(f'{REPO}/normas/{ARQ}.md')
    print('considerandos', n)
