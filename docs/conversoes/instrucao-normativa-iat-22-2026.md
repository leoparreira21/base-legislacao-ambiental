# Conversão da IN IAT nº 22/2026 — 12/10/2026

Base remota: `e11f114a2acbd1ab2db68ea63cf31550dcf40a69` (origin/main). Ramo: `norma/instrucao-normativa-iat-22-2026`.

Fonte: PDF IN 22 2026.pdf fornecido por Leo, 84 páginas, assinatura de 14/08/2026; protocolo 23.774.495-0, fls. 256–338a. Entrada 22/2026 conferida no [portal oficial do IAT](https://www.iat.pr.gov.br/Pagina/Instrucoes-Normativas-Orientacoes-Tecnicas). A transcrição usa o PDF fornecido; data/número de DIOE não confirmados em fonte primária.

## Entrega e conferência

- 70 artigos e 570 dispositivos, com IDs LexML e remissões verificadas.
- Anexo I na mãe: cinco portes × três métodos = 15 combinações autossuficientes, conferidas na imagem da página 58. Introdução e três notas em disposições próprias.
- Anexos III–VI: somente nomes dos modelos. Anexos II/VII/VIII/IX: termos de referência separados, respectivamente 44/118/105/51 disposições, sínteses e fontes.
- Âmbito de irrigação no site, 15 termos consolidados no glossário e tags regeneradas.
- IN 40/2025 tornada sem efeito pelo art. 70: ainda ausente do acervo. Nenhuma transcrição fabricada ou alteração automática de outras normas.
- Extrações Poppler simples/layout e reconstrução por posição com PyMuPDF. Quebras de página tratadas; cabeçalhos/carimbos/rodapés repetidos excluídos.
- Difflib do corpo efetivamente escrito (rótulos/IDs/tags retirados e rótulos dos wikilinks recuperados): 13.694 palavras; diferenças somente nos hífens de “requerê-las” (art. 19) e “Paraná - DER/PR” (art. 67), conferidos no PDF/layout. Após esses tratamentos documentados, igualdade do texto.
- Difflib dos arquivos reais de anexos: zero diferenças, 371/1.584/1.010/504 palavras. Marcadores gráficos dos II/IX substituídos por rótulos com IDs, transformação retirada da comparação.
- Artigos 1–70 completos; lacunas/repetições de incisos, alíneas, itens e seções documentadas na mãe. Termos de referência conferidos visualmente, sem tabelas/equações.

## Validação

- `python scripts/validar.py`: **102 documentos (40 normas, 61 anexos, 1 comentário), 0 erros, 90 avisos globais**.
- `python scripts/validar.py --afetados instrucao-normativa-iat-22-2026`: **Nenhuma outra norma aponta para dispositivos revogados/alterados desta IN**.
- `python scripts/validar.py --tags`: tags.md regenerado, 687 tags.
- `git diff --check`: sem erros.
- Site gerado; código de busca de produção executado contra seu índice: irrigação, aspersão, gotejamento e pivô central recuperam a norma; fertirrigação recupera o Anexo II. Todos os quatro anexos recuperados em irrigação. Âmbito não admite “industria argamassa”. Admitir o âmbito não fabrica ocorrência lexical no corpo.
- Scripts e protocolo de consulta não foram modificados; não houve ampliação dos testes de regressão para esta conversão documental.

## Questões para revisão

Duplicações nos arts. 14/30/35/53, itens 1/3 no art. 56 e Seções I repetidas; remissão do art. 31, V ao Anexo I para modelo do III; § 1º inexistente citado no art. 51, II. Mantida a letra publicada.

As faixas de área do Anexo I deixam pontos/intervalos sem enquadramento literal. Porte excepcional/localizada prevê MCE na LP; a [CONAMA 284/2001, art. 1º e Anexo II](https://conama.mma.gov.br/?id=282&option=com_sisconama&task=arquivo.download) classifica todos os métodos acima de 1.000 ha na categoria C e relaciona estudos de viabilidade, inclusive EIA/RIMA quando couber. Considerar também arts. 5º/13: observação para revisão jurídica, sem concluir invalidade ou revogação tácita.

Diretrizes do RAP anunciadas para disponibilização pelo IAT, sem TR correspondente neste PDF. Anexo VII conserva grafias, parêntese aberto e bibliografia publicada. Anexo IX é TR com campos exemplificativos; afirmações de conformidade não comprovam uma obra concreta. Fontes conceituais vistas apenas na busca estão identificadas nas sínteses/glossário e não apresentadas como texto integral conferido.

## Referências fora da base

As 22 referências pendentes desta conversão são:

- constituicao-federal-1988
- decreto-estadual-11977-2022
- decreto-estadual-13433-2026
- decreto-estadual-1940-1996
- decreto-estadual-2432-2019
- decreto-estadual-3813-2020
- decreto-estadual-8680-2013
- decreto-federal-6514-2008
- instrucao-normativa-iat-4-2025
- instrucao-normativa-iat-40-2025
- lei-estadual-10066-1992
- lei-estadual-16346-2009
- lei-estadual-19848-2019
- lei-estadual-19857-2019
- lei-estadual-20070-2019
- lei-federal-12787-2013
- lei-federal-6496-1977
- lei-federal-9605-1998
- resolucao-conama-1-1986
- resolucao-conama-284-2001
- resolucao-conama-503-2021
- resolucao-conama-6-1986
