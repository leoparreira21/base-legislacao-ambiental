# Conversão da IN IAT nº 38/2025

Conferência em 12/10/2026, sobre a base `e11f114a2acbd1ab2db68ea63cf31550dcf40a69`. Fonte: PDF local `IN 38 2025.pdf` enviado por Leo, 117 páginas. As instruções encontradas no PDF foram tratadas como conteúdo da norma.

## Entrega

- Norma com 109 artigos físicos, 680 dispositivos do corpo e tabelas individualizadas.
- Seis arquivos de termos de referência: IV (PCA), V (plano do uso agrícola), VI (MCE), VIII (PGRS), IX/Seção III (Projeto Agronômico), segundo X (RAP).
- Anexos normativos I, IX e primeiro X na norma-mãe; modelos II, III, VII e modelos finais do IX identificados pelo nome, com instruções normativas preservadas.
- Âmbito setorial, tags, cinco termos de glossário e lição de conversão atualizados. Nenhuma alteração ou revogação expressa de norma anterior.

## Evidências

- Extrações Poppler simples e com layout; páginas das tabelas/equações e dos termos conferidas visualmente.
- `difflib` entre o corpo do arquivo final e a extração com layout, retirando rótulos/IDs/tags, recuperando rótulos dos links e normalizando espaços: 14.963 tokens em cada lado, zero diferenças. As tabelas foram comparadas separadamente às imagens.
- Comparações independentes dos termos IV, V, VI, VIII, IX/Seção III e RAP com os arquivos efetivamente gravados: zero diferenças após normalizações de formatação documentadas. Nos demais textos do IX foram conferidas a Seção V e as recomendações de transporte.
- Corpo: cinco tabelas, 14 + 11 + 3 + 5 + 11 linhas. Anexo I: duas tabelas de cinco linhas. Anexo IX: cinco tabelas, 8 + 2 + 9 + 23 + 4 entradas; sete expressões. Primeiro X: três tabelas, 30 + 30 + 5 linhas. PCA: cabeçalho de quadro com sete colunas, duas linhas de preenchimento vazias.
- `python scripts/validar.py`: 104 documentos, zero erros, 91 avisos globais de referências fora da base.
- `python scripts/validar.py --tags`: catálogo atualizado.
- `python scripts/validar.py --afetados instrucao-normativa-iat-38-2025`: nenhuma outra norma aponta para dispositivos revogados/alterados.
- `python scripts/gerar_site.py`: geração concluída, 104 arquivos e 6.867 trechos; norma presente em `_site/index.json` e âmbito em `_site/ambitos.json`.
- `python scripts/consultar.py 'lodo gerenciamento' --limite 3`: recupera a norma e seu plano de gerenciamento agrícola.
- `git diff --check`: sem erros. Não houve mudança em scripts de consulta/validação.

## Questões para revisão

As notas da norma e dos termos detalham a numeração duplicada/trocada, remissões a anexos divergentes, Tabela 8 ausente, palavras coladas, trecho de criação animal no MCE, trechos de solo efetivamente recortados na página 108 e fórmulas com `K_Kj`/parcela amoniacal ausente. Os textos foram preservados ou limitados ao conteúdo legível, sem preenchimento por inferência. O título informa 28/04/2025; a assinatura digital é de 30/05/2025; publicação no DIOE não identificada no PDF. Diferenças frente à CONAMA 498/2020 estão separadas em observação do conversor, sem inferência de revogação.

## Referências pendentes desta conversão

22 normas distintas ainda fora do acervo:

`decreto-estadual-11977-2022`, `decreto-estadual-1940-1996`, `decreto-estadual-3813-2020`, `decreto-estadual-5503-2002`, `decreto-estadual-8680-2013`, `decreto-estadual-9415-2025`, `decreto-federal-6514-2008`, `instrucao-normativa-mapa-10-2004`, `lei-estadual-10066-1992`, `lei-estadual-16346-2009`, `lei-estadual-19848-2019`, `lei-estadual-19857-2019`, `lei-estadual-20070-2019`, `lei-estadual-7109-1979`, `lei-federal-9605-1998`, `portaria-dnpm-231-1998`, `portaria-iap-212-2019`, `resolucao-conama-481-2017`, `resolucao-conama-498-2020`, `resolucao-conama-6-1986`, `resolucao-conama-313-2002`, `resolucao-sema-2-2025` (órgão conforme publicado no PCA; não substituído por SEDEST).
