# Conversão da IN IAT nº 23/2026 — 12/10/2026

Base remota: `cff6ec81e810b2320c02bfe1d36ba1c1a04de96e` (origin/main). Ramo: `norma/instrucao-normativa-iat-23-2026`.

Fonte: PDF IN 23 2026.pdf fornecido por Leo, 81 páginas, assinatura de 14/08/2026, protocolo 23.757.475-3, folhas 192–271a. Entrada e [PDF oficial do IAT](https://www.iat.pr.gov.br/sites/agua-terra/arquivos_restritos/files/documento/2026-08/instrucao_normativa_23-2026-estabelece_definicoes-criterios-diretrizes_e_procedimentos_para_o_licenciamento_ambiental_de_empreendimentos_de_bovinocultura_no_estado_do_parana.pdf) abertos em 12/10/2026. Data/número de publicação no DIOE não constam do PDF e não foram confirmados.

## Entrega e conferência

- 79 artigos, 616 dispositivos, sequência de artigos 1–79 e sequências de parágrafos, incisos, itens e alíneas conferidas. Sem IDs duplicados. Incisos de classificação do art. 2º vinculados ao caput, preservando a posição do parágrafo único intercalado.
- Anexos I/X normativos na mãe. Anexo I: tabelas editoriais 1–4 com 5/5/5/9 linhas de dados. Anexo X: 22 disposições, modelo da Tabela 1, parte quantitativa da Tabela 2 e 14 linhas na Tabela 3. Células mescladas repetidas e continuidade entre pp. 79–80 reunida. Tabelas conferidas nas imagens; sem fórmulas ou figuras normativas indispensáveis.
- Anexos III–VII: nomes dos modelos. Anexos II/VIII/IX: termos de referência em arquivos separados, 46/56/29 entradas, com síntese interpretativa e fontes separadas.
- Âmbito setorial, três expressões sinônimas para busca, três conceitos no glossário e tags regeneradas. Corrigida falta preexistente de `],` entre irrigação e lodo em `consultas/ambitos.json`, que impedia geração do site.
- Efeito expresso do art. 79: IN IAT 35/2025 tornada sem efeito, ainda fora do acervo; relação registrada sem transcrição fabricada.
- Extrações Poppler simples e layout; quebras de página tratadas explicitamente, cabeçalhos/carimbos/rodapés repetidos retirados. Imagens dos anexos técnicos e dos quadros conferidas.
- Difflib do corpo do Markdown real, após retirar rótulos/IDs/tags e recuperar rótulos dos wikilinks: 13.416 palavras da extração vs 13.415 no Markdown; única diferença “requerê- las” → “requerê-las”, união de quebra de linha documentada. Nenhum conteúdo lexical acrescentado ou omitido.
- Difflib do texto corrido do Anexo X real: 1.213 palavras em ambas as versões, zero diferenças após reunião documentada de palavras hifenizadas e unidade fragmentada. Contagens das tabelas verificadas no arquivo escrito.
- Difflib dos anexos técnicos reais: MCE 478 palavras e laudo com zero diferenças; PCA 621 palavras em ambas as versões, única diferença “no” extraído → “nº”, ordinal conferido na imagem e documentado.

## Validação

- `python scripts/validar.py`: **113 documentos (42 normas, 70 anexos, 1 comentário), 0 erros, 95 avisos globais**.
- `python scripts/validar.py --afetados instrucao-normativa-iat-23-2026`: **Nenhuma outra norma aponta para dispositivos revogados/alterados desta IN**.
- `python scripts/validar.py --tags`: tags.md regenerado, 690 tags.
- `git diff --check`: sem erros.
- Site gerado. Funções de produção executadas contra o índice: bovinocultura, gado leiteiro, recria de novilha e confinamento bovino recuperam a norma. Anexos MCE/PCA/laudo recuperados com atividade bovinocultura e termos memorial/controle/laudo. Âmbito alheio (“industria argamassa”) não admite esta IN.
- Scripts e protocolo de consulta não foram modificados.

## Questões para revisão

- Art. 51, II: remissão a § 1º inexistente; mantida sem link presumido.
- Anexo I: RAP “Preliminar” no quadro e “Prévio” na nota, com diretrizes futuras pelo IAT; o PDF não fornece esse TR.
- Anexo II: seção III ausente na numeração publicada.
- Anexo VIII: título “PLANOS DE CONTROLE AMBIENTAL” difere da relação de anexos; “ver item x” não identifica destino.
- Anexo IX: frase final interrompida em “visualizar claramente”; nenhum complemento inventado.
- Anexo X: itens “1.” repetidos, grafia “Melhich–1”, declive “20 30%”, “profundiddade” e grau “3–MUITO FORTE” preservados. Quadro de preenchimento com opções >120/>90/>60 difere dos limites textuais 95/200 mg.dm–3; não harmonizado pelo conversor.
- Vigência vinculada à publicação; assinatura não tomada como data de publicação. Transição exige análise do processo concreto, inclusive art. 173 do Decreto 9.541/2025.

## Referências fora da base

19 referências pendentes na norma e nos anexos:

- constituicao-federal-1988
- decreto-estadual-11977-2022
- decreto-estadual-13433-2026
- decreto-estadual-1940-1996
- decreto-estadual-3813-2020
- decreto-estadual-5503-2002
- decreto-estadual-8680-2013
- instrucao-normativa-iat-35-2025
- instrucao-normativa-mapa-61-2020
- lei-estadual-10066-1992
- lei-estadual-19857-2019
- lei-estadual-20070-2019
- lei-estadual-7109-1979
- lei-federal-11326-2006
- lei-federal-6496-1977
- lei-federal-9605-1998
- portaria-conjunta-iat-adapar-1-2023
- portaria-iap-256-2013
- resolucao-conama-6-1986
