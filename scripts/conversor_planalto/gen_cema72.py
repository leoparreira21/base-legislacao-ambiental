import sys, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from estadual import link_estadual, post_considerandos, REPO
ARQ = 'resolucao-cema-72-2009'
L = lambda t: link_estadual(t, ARQ)
T = [
('Abatedouro de aves','3000 aves/mês'),('Abatedouro de suínos','60 cabeças/mês'),('Abatedouro de bovinos','30 cabeças/mês'),('Abatedouro de ovinos','60 cabeças/mês'),
('Unidade de processamento de peixes, moluscos, anfíbios e crustáceos','200 Kg de carne processada/dia'),('Unidade de classificação de ovos','300 dúzias/dia'),
('Fabrica de embutidos e defumados','1000 Kg de carne processada/dia'),('Laticínios (resfriamento e envase)','1250 l de leite/dia'),('Laticínios (queijo e manteiga)','800 l de leite/dia'),
('Laticínios (doce de leite)','800 l de leite/dia'),('Fabrica de conservas salgadas','250 Kg de matéria prima/dia'),('Fabrica de geléias conservas doces','250 Kg de matéria prima/dia'),
('Açúcar mascavo e rapadura','3000 Kg de cana moída/dia'),('Indústria de doces, chocolates, balas','200 Kg de produto/dia'),('Industria de processamento de frutas','500 l de suco/dia'),
('Industria de biscoitos e bolachas','300 Kg de produto/dia'),('Industria de beneficiamento de madeira','10 funcionários'),('Industria de farinha de mandioca','500 Kg de mandioca/dia'),
('Transbordo e armazenamento de cereais em áreas rurais','500 t (capacidade de estocagem)'),('Ervateira','10 funcionários'),('Industria cerâmica','10 funcionários'),
('Industria de farinha de milho','100 Kg de milho/dia'),('Produção de vinho','2000 Kg de uva processada/dia'),('Produção de vinagre','300 l/dia'),('Produção de sucos','600 l/dia'),
('Destilaria de álcool e cachaça','1000 Kg de cana moída/dia'),('Torrefação e empacotamento de chá','50 Kg de chá/dia'),('Torrefação e empacotamento de café','120 Kg de matéria/dia'),
('Tratamento de superfície','Até 10 m3/dia(1)'),('Unidade de processamento de mel','12.000 Kg de mel/ano'),
('Fornos para produção de carvão','Empreendimentos até 5 (cinco) fornos de carvão, com capacidade máxima de processamento de 20 m3/mês de lenha/forno (2)')]
D = ('Matrícula ou Transcrição do Cartório de Registro de Imóveis em nome do requerente, e em caso de imóvel locado no nome do locador junto com o contrato de locação, no máximo de 90 (noventa) dias, para imóveis rurais exige-se a averbação da Reserva Legal junto à matrícula do imóvel, ou Documento de propriedade ou justa posse rural ou conforme exigências constantes da Seção VI, art.46 a 57 da Resolução CEMA 065 de 01 de julho de 2008')
R70 = lambda a, t: f'[[resolucao-cema-70-2009#{a}|{t}]]'
def q(id_, rot, linhas):
    o = [f'> **Nova redação – {rot}** {{#{id_}}}']
    for i, l in enumerate(linhas):
        o.append('> ' + l if i == 0 else '>')
        if i: o[-1] = '> ' + l if False else o[-1]
    return o
def quote(id_, rot, linhas):
    o = [f'> **Nova redação – {rot}** {{#{id_}}}']
    for l in linhas:
        o.append('> ' + l); o.append('>')
    o.pop()
    return o
CEMA65 = '[[resolucao-cema-65-2008|Resolução CEMA 065 de 01 de julho de 2008]]'
Dl = D.replace('Resolução CEMA 065 de 01 de julho de 2008', CEMA65)
out = ['---','norma: Resolução CEMA nº 72/2009',f'arquivo: {ARQ}','tipo: resolucao','esfera: estadual','uf: PR',
'orgao: Conselho Estadual do Meio Ambiente – CEMA/PR','numero: 72','ano: 2009','data_assinatura: 2009-10-22','data_publicacao: 2009-10-22',
'publicacao: Diário Oficial nº 8082, de 22/10/2009','vigencia: na data da publicação (art. 7º)',
'ementa: "Re-ratificação da Resolução CEMA nº. 070/2009, que dispõe sobre o licenciamento ambiental para Empreendimentos Industriais, haja vista revisão do texto de alguns dos artigos da referida norma."',
'situacao: vigente','regulamenta: []','regulamentado_por: []','altera: ["[[resolucao-cema-70-2009]]"]','alterado_por: []','revoga: []','revogado_por: []',
'cita: []','tags: []',
'fonte: "Impressão de página da internet em PDF (2 páginas, portal de legislação estadual), enviada por Leo; o rodapé traz \\"Este texto não substitui o publicado no Diário Oficial do Estado\\""','---','',
'# Resolução CEMA nº 72, de 22 de outubro de 2009 {#resolucao-cema-72-2009}','',
'> **Ementa:** Re-ratificação da Resolução CEMA nº. 070/2009, que dispõe sobre o licenciamento ambiental para Empreendimentos Industriais, haja vista revisão do texto de alguns dos artigos da referida norma.','',
'**Preâmbulo** {#preambulo} ' + L('O CONSELHO ESTADUAL DO MEIO AMBIENTE, no uso das suas atribuições conferidas pela Lei Estadual nº 7.978, de 30 de novembro de 1984, alterada pelas leis nº 8.289, de 07 de maio de 1986 e 8.485, de 03 de junho de 1987 e 11.352, de 13 de fevereiro de 1.996, pelo disposto no Decreto nº 4.447, de 12 de julho de 2.001 e;'),'',
'Considerando a necessidade de revisão do texto dos artigos 5º, 6º, 7º, 8º e 9º da Resolução n.º 070/2009, cuja alteração não afeta o conteúdo da norma, de modo que a sua segurança jurídica resta preservada.','',
'RESOLVE:','']
# Art 1
out += ['###### Art. 1º {#art1}','',
 f'**Art. 1º, caput** {{#art1_cpt}} Alterar a redação do caput do Art.5º da Resolução 070/2009, que passa a vigorar com a seguinte redação:'.replace('Art.5º da Resolução 070/2009', f'{R70("art5_cpt","Art.5º")} da [[resolucao-cema-70-2009|Resolução 070/2009]]'),'']
out += quote('art1_cpt_alt1','Resolução CEMA nº 70/2009, art. 5º, caput',['“Art. 5º. Ficam passíveis de licenciamento ambiental simplificado os empreendimentos com as características constantes no quadro abaixo.”']) + ['']
out.append('- **Art. 1º, Tabela 1, cabeçalho** {#art1_tab1_cab} Empreendimento/Atividade | Volume de transformação ou produção (limite máximo) ou numero Maximo de funcionários')
for i,(a,b) in enumerate(T,1):
    out.append(f'- **Art. 1º, Tabela 1, linha {i}** {{#art1_tab1_lin{i}}} Empreendimento/Atividade: {a} | Volume de transformação ou produção (limite máximo) ou numero Maximo de funcionários: {b}')
out += ['- **Art. 1º, Tabela 1, observações** {#art1_tab1_obs} (1) Vazão de efluentes líquidos gerados no processo | (2) Limite máximo/ano | (3) Não serão permitidas instalações de fornos para produção de carvão em área urbana.','']
# Art 2
out += ['###### Art. 2º {#art2}','',
 f'**Art. 2º, caput** {{#art2_cpt}} Altera-se a redação do item “d” e” e” do inciso I do {R70("art6_cpt_inc1","art.6º")}, que trata do requerimento de Licença Ambiental Simplificada – LAS, que passa a vigorar com a seguinte redação:','']
out += quote('art2_cpt_alt1','Resolução CEMA nº 70/2009, art. 6º, inciso I, alíneas "d" e "e"',['“Art.6º...........','I. LICENÇA AMBIENTAL SIMPLIFICADA - LAS',f'd) {Dl} ;'.replace(' ;',';'),'e) Nos casos devidamente justificados em que não seja possível a apresentação dos documentos especificados no item d, os mesmos deverão ser apresentados antes do inicio da operação da atividade ou empreendimento sob pena de cancelamento da licença Ambiental;']) + ['']
# Art 3
out += ['###### Art. 3º {#art3}','',
 f'**Art. 3º, caput** {{#art3_cpt}} Altera-se a redação do caput do {R70("art7_cpt","art.7º")}, e a redação do item “d” e “e” do inciso I do referido artigo, que passam a vigorar com a seguinte redação:','']
out += quote('art3_cpt_alt1','Resolução CEMA nº 70/2009, art. 7º, caput e inciso I, alíneas "d" e "e"',['“Art. 7º Os Empreendimentos Industriais não compreendidos nos Artigos 4º e 5.º deverão requerer as Licenças Prévia, de Instalação e de Operação.','I. LICENÇA PRÉVIA',f'd) {Dl};','e) Nos casos devidamente justificados em que não seja possível a apresentação dos documentos especificados no item d, os mesmos deverão ser apresentados antes do inicio da operação da atividade ou empreendimento sob pena de cancelamento do Licenciamento ambiental já realizado.”']) + ['']
# Art 4
out += ['###### Art. 4º {#art4}','',
 f'**Art. 4º, caput** {{#art4_cpt}} Altera-se a redação do caput do {R70("art8_cpt","art.8º")} e a redação da letra “e” e a supressão da letra “ f” do inciso I e II do referido artigo, que trata de empreendimentos já instalados, e passam a vigorar com a seguinte redação:','']
out += quote('art4_cpt_alt1','Resolução CEMA nº 70/2009, art. 8º',['“Art.8º - onde se lê parágrafo única, leia -se parágrafo único.','I. LICENÇA AMBIENTAL SIMPLIFICADA – LAS DE REGULARIZAÇÃO',f'e) {Dl};','II. LICENÇA DE OPERAÇÃO- LO DE REGULARIZAÇÃO',f'e) {Dl}.”']) + ['']
# Art 5-7
out += ['###### Art. 5º {#art5}','',
 f'**Art. 5º, caput** {{#art5_cpt}} Altera-se a redação do caput do {R70("art9_cpt","art.9º")}','']
out += quote('art5_cpt_alt1','Resolução CEMA nº 70/2009, art. 9º, caput',['“Art.9º - onde se lê Art.6º leia-se Art. 6º, 7º e 8º desta Resolução”.']) + ['']
out += ['###### Art. 6º {#art6}','','**Art. 6º, caput** {#art6_cpt} Ficam ratificadas as demais cláusulas constantes da [[resolucao-cema-70-2009|Resolução Nº 070/2009-CEMA]].','',
 '###### Art. 7º {#art7}','','**Art. 7º, caput** {#art7_cpt} Esta Resolução entra em vigor na data de sua publicação, ficando revogadas as demais disposições em contrário.','',
 '---','','**Fecho** {#fecho} Curitiba, 22 de outubro de 2009.','',
 '**Assinaturas** {#assinaturas} Lindsley da Silva Rasca Rodrigues – Secretário de Estado do Meio Ambiente e Recursos Hídricos; Lindsley da Silva Rasca Rodrigues – Presidente do Conselho Estadual do Meio Ambiente','',
 '---','',
 '## Relação com outras normas {#relacao-outras-normas}','','Observação do conversor (não é texto normativo):','',
 '- Altera os arts. 5º a 9º da Resolução CEMA nº 70/2009 (fora da base). A CEMA 70/2009 consta como revogada pelo [[decreto-estadual-9541-2025]]; este decreto não cita a Resolução CEMA 72/2009, que ficou sem objeto próprio (revogação tácita a conferir pelo usuário).',
 '- O art. 6º (“cláusulas constantes da Resolução Nº 070/2009”) e as alíneas “d” e “e” remetem à Seção VI, arts. 46 a 57, da [[resolucao-cema-65-2008]], revogada por inteiro pela [[resolucao-cema-105-2019]] (fora da base).','',
 '## Notas de transcrição {#notas-transcricao}','',
 'Fonte: impressão de página do portal de legislação estadual em PDF (2 páginas) enviada por Leo; o cabeçalho traz “Resolução CEMA nº 072 - 22 de Outubro de 2009” e “Publicado no Diário Oficial nº. 8082 de 22 de Outubro de 2009”; o rodapé traz “Este texto não substitui o publicado no Diário Oficial do Estado”.','',
 '- Tabela do art. 1º lida da imagem da página: 31 linhas, mais o cabeçalho (`art1_tab1_cab`) e as notas (1) a (3) (`art1_tab1_obs`). A nota (3) não tem chamada na tabela do original.',
 '- Aspas: o art. 2º abre a citação (“Art.6º...........) e não a fecha; mantido como publicado. As reticências do original (“Art.6º...........”) indicam trecho não alterado.',
 '- Grafias e expressões do original mantidas: “numero Maximo”, “Fabrica”, “geléias conservas doces”, “d” e” e”, “ f”, “leia -se”, “parágrafo única”, “Industria”.',
 '- O art. 1º e os arts. 2º a 5º trazem as novas redações em citação, com ID `_alt1` e links para os dispositivos da CEMA 70/2009 (ainda fora da base, links pendentes).',
 '- A remissão “Resolução CEMA 065 de 01 de julho de 2008” foi ligada à [[resolucao-cema-65-2008]].',
 '- Preâmbulo: o texto não numera os considerandos; o único “Considerando” foi mantido como parágrafo do preâmbulo.']
open(f'{REPO}/normas/{ARQ}.md','w').write('\n'.join(out)+'\n')
n=post_considerandos(f'{REPO}/normas/{ARQ}.md'); print('ok',n)
