# Lote de 20 PDFs — material preliminar para revisão

Registro autorizado pelo usuário. O pacote e o relatório abaixo preservam o estado preliminar entregue em 10/11/2026. As observações sobre ausência de commit no relatório descrevem o estado da entrega original; este commit apenas arquiva esse material, sem incorporar as normas ao corpus de consulta.

Validação estrutural repetida antes deste registro: 25 arquivos Markdown, 0 erros e 23 avisos de referências externas ao lote. Permanecem pendentes a conferência dos PDFs, nove quadros e 39 referências de anexos ausentes. A validação global do acervo não é certificada por este registro.

O arquivo `Lote_20_PDFs_Markdown_PRELIMINAR.zip` contém os 20 rascunhos, cinco anexos técnicos, HTML de revisão, fontes textuais, registros de pendências e proposta de âmbitos. O conteúdo é preliminar e não foi publicado no site.

---

# Lote de 20 PDFs — conversão preliminar para revisão

**Estado: conversão parcial, não pronta para commit ou incorporação à base.**

Foram lidos os 20 documentos (143 páginas) e preparados 20 arquivos de normas, cinco arquivos de anexos técnicos e 20 páginas HTML. 10 normas foram identificadas como revogadas pelas relações expressas já existentes no acervo. As demais mantêm situação cadastral provisória, sem certificação externa de vigência.

A validação estrutural local dos 25 arquivos Markdown terminou com 0 erros. Isso não certifica fidelidade, completude do texto ou validade jurídica. A validação integrada do repositório inteiro não foi concluída.

## Pendências que impedem finalizar

- Não foi possível obter os bytes dos PDFs nem visualizar as imagens dos quadros. Por isso, a comparação palavra por palavra com a extração `pdftotext`, a identificação visual de tachados e a conferência de células mescladas continuam pendentes.
- 39 referências de anexos estão ausentes ou sem conteúdo identificável nos PDFs recebidos. Foram registradas sem inventar texto. A quantidade é de referências, não necessariamente de anexos distintos.
- 9 quadros ou tabelas no corpo tiveram o conteúdo retirado da camada normativa do rascunho e preservado em `quadros-pendentes.json` e `fontes-texto/`. A posição foi marcada com uma nota editorial.
- Os anexos normativos de CONAMA 6/1987, CONAMA 2/1994 e IAP 38/2010 precisam de transcrição visual. A simbologia do Anexo I da CONAMA 401/2008 também precisa ser conferida. O texto extraído está em `anexos-manifest.json` e em `fontes-texto/`.
- As redações sucessivas explicitadas nas fontes foram tratadas como texto compilado preliminar. Toda remoção de redação anterior deve ser revista contra os tachados/diagramação originais.
- Remissões internas e externas foram vinculadas onde identificáveis; o rascunho não certifica exaustividade de todos os wikilinks. As referências fora deste pacote estão em `validacao-estrutura.json`.
- Não houve commit, push, publicação nem modificação do repositório remoto.

## Divergências que exigem revisão

- `conama 335 2005.pdf` contém a Resolução CONAMA nº 335, de 3 de abril de 2003; o arquivo gerado usa 2003.
- SEDEST 32/2022: cabeçalho de 03/06/2022 e fecho de 30/05/2022.
- SEDEST 51/2019: cabeçalho de 19/11/2019 e fecho de 15/07/2019; Anexo I é citado como certidão e PCA.
- Resolução conjunta de irrigação 18/2020: cabeçalho de 14/08/2020 e fecho de 12/08/2020; há duas redações do art. 24. O slug foi harmonizado com a referência já existente no acervo.
- SEDEST 50/2022: Anexo XI é citado para documentos distintos. Os números de anexos não foram inferidos de nomes de arquivos externos.
- IAT 170/2020: dois incisos III no art. 13. O texto de ambos foi preservado com sufixo técnico no segundo ID.
- IAP 187/2013, Anexo VI: numeração 1.2 repetida, mantida no texto.
- SEDEST 16/2020: o texto cita Resolução SEMA nº 054, de 19/11/2019; mantida a referência literal, sem correção de órgão por inferência.
- As cláusulas “revogadas as disposições em contrário” não geraram revogação tácita automática.

## Inventário

| PDF fornecido | Arquivo Markdown | Situação segundo o acervo | Artigos |
|---|---|---|---|
| portaria IAP 216 2018.pdf | [portaria-iap-216-2018](normas/portaria-iap-216-2018.md) | revogada | 19 |
| portaria IAT 170 2020.pdf | [portaria-iat-170-2020](normas/portaria-iat-170-2020.md) | vigente | 29 |
| conama 6 1987.pdf | [resolucao-conama-6-1987](normas/resolucao-conama-6-1987.md) | vigente | 13 |
| sedest 32 2022.pdf | [resolucao-sedest-32-2022](normas/resolucao-sedest-32-2022.md) | revogada | 14 |
| portaria IAP 212 2019.pdf | [portaria-iap-212-2019](normas/portaria-iap-212-2019.md) | revogada | 23 |
| Resolução Conjunta IBAMA SEMA IAP 007 2008.pdf | [resolucao-conjunta-ibama-sema-iap-7-2008](normas/resolucao-conjunta-ibama-sema-iap-7-2008.md) | vigente | 15 |
| portaria IAP 38 2010.pdf | [portaria-iap-38-2010](normas/portaria-iap-38-2010.md) | vigente | 28 |
| conama 002 1994.pdf | [resolucao-conama-2-1994](normas/resolucao-conama-2-1994.md) | vigente | 6 |
| conama 335 2005.pdf | [resolucao-conama-335-2003](normas/resolucao-conama-335-2003.md) | vigente | 18 |
| conama 401 2008.pdf | [resolucao-conama-401-2008](normas/resolucao-conama-401-2008.md) | vigente | 28 |
| portaria IAP 187 2013(1).pdf | [portaria-iap-187-2013](normas/portaria-iap-187-2013.md) | revogada | 18 |
| resolução conjunta SEDEST IAT 22 2021(1).pdf | [resolucao-conjunta-sedest-iat-22-2021](normas/resolucao-conjunta-sedest-iat-22-2021.md) | vigente | 20 |
| sedest 51 2019(1).pdf | [resolucao-sedest-51-2019](normas/resolucao-sedest-51-2019.md) | revogada | 15 |
| portaria IAP 155 2013(1).pdf | [portaria-iap-155-2013](normas/portaria-iap-155-2013.md) | revogada | 13 |
| conama 428 2010(1).pdf | [resolucao-conama-428-2010](normas/resolucao-conama-428-2010.md) | vigente | 9 |
| sedest 32 2020(1).pdf | [resolucao-sedest-32-2020](normas/resolucao-sedest-32-2020.md) | revogada | 29 |
| sedest 16 2020(1).pdf | [resolucao-sedest-16-2020](normas/resolucao-sedest-16-2020.md) | revogada | 23 |
| Resolução Conjunta SEDEST SEAB IAT IAPAR-EMATER-IDR 18 2020(1).pdf | [resolucao-conjunta-sedest-seab-iat-iapar-18-2020](normas/resolucao-conjunta-sedest-seab-iat-iapar-18-2020.md) | revogada | 24 |
| sedest 50 2022(1).pdf | [resolucao-sedest-50-2022](normas/resolucao-sedest-50-2022.md) | vigente | 35 |
| sedest 08 2021(1).pdf | [resolucao-sedest-8-2021](normas/resolucao-sedest-8-2021.md) | revogada | 45 |

## Normas revogadas identificadas

| Norma | Ato revogador já registrado no acervo |
|---|---|
| portaria-iap-216-2018 | instrucao-normativa-iat-17-2025 |
| resolucao-sedest-32-2022 | decreto-estadual-9541-2025 |
| portaria-iap-212-2019 | portaria-iat-33-2022 |
| portaria-iap-187-2013 | instrucao-normativa-iat-30-2025 |
| resolucao-sedest-51-2019 | decreto-estadual-9541-2025 |
| portaria-iap-155-2013 | instrucao-normativa-iat-31-2025 |
| resolucao-sedest-32-2020 | resolucao-sedest-39-2024 |
| resolucao-sedest-16-2020 | decreto-estadual-9541-2025 |
| resolucao-conjunta-sedest-seab-iat-iapar-18-2020 | decreto-estadual-9541-2025 |
| resolucao-sedest-8-2021 | decreto-estadual-9541-2025 |

## Quadros no corpo pendentes

| Norma | Dispositivo |
|---|---|
| resolucao-sedest-32-2022 | Art. 7 |
| resolucao-sedest-32-2022 | Art. 8 |
| portaria-iap-212-2019 | Art. 4 |
| portaria-iap-212-2019 | Art. 5 |
| resolucao-sedest-51-2019 | Art. 6 |
| resolucao-sedest-32-2020 | Art. 4 |
| resolucao-sedest-16-2020 | Art. 5 |
| resolucao-conjunta-sedest-seab-iat-iapar-18-2020 | Art. 4 |
| resolucao-sedest-50-2022 | Art. 5 |

## Como revisar

Abra `html/index.html` para navegar nas normas. As cinco diretrizes técnicas aparecem integradas nas páginas das normas-mãe e continuam separadas em `normas/anexos/`.

Use `fontes-texto/` para recuperar o texto extraído sem alterações. Essa extração é material de trabalho, não substitui os PDFs originais nem constitui transcrição normativa validada.

Após conferir imagens e completar os anexos necessários: rever metadados, tags e wikilinks; aplicar relações recíprocas no acervo completo; integrar a proposta de âmbitos; regenerar tags e HTML do repositório inteiro; rodar o validador e `--afetados`; submeter a revisão antes do commit.

A proposta em `integracao/ambitos-lote20.proposta.json` contém somente os acréscimos sugeridos. Não deve substituir o arquivo completo de âmbitos. As páginas e o catálogo deste pacote servem apenas à revisão do lote.

## Referência do acervo consultado

Metadados e relações consultados no commit [27f5e2703e5ecd1b41d8405e7cde3fd21ee78474](https://github.com/leoparreira21/base-legislacao-ambiental/tree/27f5e2703e5ecd1b41d8405e7cde3fd21ee78474). As fontes normativas desta conversão são exclusivamente os 20 PDFs fornecidos e o conteúdo já presente no repositório.

