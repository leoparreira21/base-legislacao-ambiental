# Revisão de tags — 07/11/2026

> Registro da etapa inicial. A [continuidade de 08/11/2026](continuidade-2026-11-08.md) apresenta a cobertura e os resultados mais recentes.

## Resultado e limite de cobertura

**Entrega parcial da revisão semântica solicitada.** Inventário automático dos 183 documentos e leitura das ementas das 75 normas; proposta de organização para todo o vocabulário remanescente. Leitura detalhada do texto da CONAMA 430/2011 presente no repositório, com 18 decisões por artigo. Normalização lexical em outras três normas. Não foi concluída a revisão dispositivo a dispositivo das outras 74 normas, dos 107 anexos e do comentário. Não houve conferência com novas publicações oficiais nem certificação de vigência externa.

Snapshot: `dd1afa60af30ec87cf92609520fb0015c7bf8117`. A cobertura individual está em `inventario-documentos.json`; alterações em `alteracoes.json`; decisões e fundamentos em `decisoes-conama430.json`. A taxonomia é uma proposta, ainda não integrada ao motor de busca.

| Medida | Antes | Depois |
|---|---:|---:|
| Tags distintas efetivamente usadas no corpo | 825 | 819 |
| Ocorrências de tags no corpo | 39.853 | 39.843 |
| Tags distintas no frontmatter da CONAMA 430 | 55 | 46 |
| Normas alteradas | — | 4 |
| Tags novas criadas | — | 0 |

O catálogo `tags.md` anterior listava 837 tags. A regeneração sem modificar os textos já produziria 825: não contabilizar essa diferença como remoção desta revisão. Extração exclui IDs, wikilinks e exemplos em código, seguindo o validador existente. Os 43.382 IDs são identificadores estruturais, incluindo títulos e seções editoriais; não são uma contagem de dispositivos jurídicos independentes. A redução global efetiva é 0,73%; **a redução substancial pretendida ainda não foi realizada**. No piloto, a redução do vocabulário é de 16,36%.

## Estrutura recomendada

Uma floresta de facetas permite combinar assunto, atividade e função sem criar uma tag para cada combinação:

```text
Tema
├── Água e recursos hídricos
├── Efluentes
│   ├── Esgoto sanitário
│   ├── Padrões de lançamento
│   ├── Ecotoxicidade
│   └── Reuso
├── Resíduos
├── Ar e ruído
├── Vegetação e território
├── Radiação
└── Segurança e saúde
Atividade
├── Agropecuária → bovinocultura / suinocultura / avicultura
├── Aquicultura → maricultura
└── Indústria e serviços
Instrumento
├── Licenciamento → licenças → LP / LI / LO
├── Estudos e documentos
└── Procedimentos administrativos
Parâmetro técnico e monitoramento
├── DBO / DQO / fósforo / óleos e graxas
└── Monitoramento → automonitoramento
Instituição
Controle editorial → revogado / incluído / redação alterada
```

O JSON `consultas/taxonomia-tags.proposta.json` organiza as 819 tags em ramos e define relações de termo mais amplo em um subconjunto. Os demais termos são folhas do grupo. **Grupo é organização para navegação**, não prova de que um conceito seja subtipo de outro. `pai` é uma relação semântica explícita e separada. Essa distinção evita afirmar que DBO seja um tipo de efluente ou que uma licença seja um tipo de atividade industrial. O arquivo `arvore.md` lista todo o vocabulário.

Os termos de função (`vigencia`, `revogacao`, `prazo`, `ambito-aplicacao`) e instituições devem ser facetas secundárias. Não retirar esses marcadores globalmente antes de preservar sua informação no índice. Manter as tags de controle: os leitores atuais dependem de `revogado`. Não converter tags em caminhos com `/` nos arquivos normativos: os parsers atuais esperam slugs com hífen. A hierarquia fica no JSON.

## Alterações efetivas

- `licenca-previa` → `lp`; `licenca-instalacao` → `li`; `licenca-operacao` → `lo`: IN IBAMA 19/2018 (arts. 6–10 e 12) e CONAMA 382/2006 (art. 6). São nomes por extenso das licenças, não equivalência de regimes estaduais e federais.
- `termo-ajustamento-conduta` → `tac`: Lei PR 16.346/2009, art. 7, I. O próprio dispositivo nomeia o instrumento.
- `aplicabilidade` → `ambito-aplicacao`: CONAMA 382/2006, art. 6, que delimita as fontes abrangidas pela data de solicitação da LI.
- CONAMA 430/2011: troca de tags genéricas por objeto específico e eliminação de redundâncias nos artigos discriminados no registro de decisões.

Exemplos do piloto:

| Referência | Problema | Decisão |
|---|---|---|
| Art. 6 | Só `prazo` não representa a autorização excepcional de lançamento fora dos padrões | `padrao-lancamento` + `condicao-especial` |
| Art. 24, § 2º | `dispensa` pode induzir a consulta a dispensa de licença | `automonitoramento` + `baixo-potencial-poluidor`; conservar integralmente a condição no texto |
| Art. 26 | Documento efetivo é laudo analítico | Substituir `laudo-tecnico` por `laudo-analitico` |
| Art. 29 | Adequação de empreendimentos existentes em prazo transitório | `transicao` + `prorrogacao-prazo` |
| Art. 32 | Ausência de tag para ato que revoga outra norma | `revogacao`, nunca `revogado` |

Não fundir sem análise: destinação/disposição final; resíduo/rejeito; dispensa/inexigibilidade; licença/autorização; padrões de emissão/qualidade; LAE federal/AA paranaense. COV e VOC parecem variantes lexicais, mas as definições e escopos normativos precisam ser confrontados antes da normalização global. Tags raras não são automaticamente inúteis.

## Contrato proposto para a busca por IA

1. A consulta deve declarar pelo menos uma tag canônica de tema ou instrumento e registrar o termo original e os aliases usados. Termo desconhecido deve gerar desambiguação; não inventar tag.
2. Combinar OR dentro de uma faceta e AND entre facetas explicitamente exigidas pelo caso. Não exigir atividade em normas transversais. Usar `ambitos.json` e ementa como controle de contexto.
3. Expandir uma tag mais ampla para descendentes explicitamente modelados. Não expandir irmãos nem transformar `grupo` em equivalência. Registrar a expansão para auditoria. Instituições e controle editorial não devem ampliar temas.
4. Distinguir `tags_diretas`, `tags_contexto` e `tags_agregadas`. Tags agregadas do artigo servem para localizar o artigo; não devem ser atribuídas a todos os filhos como se fossem diretas.
5. A recuperação deve carregar caput, condições, exceções, remissões e tabelas necessárias. A tag classifica o assunto; não informa se o dispositivo exige, dispensa ou proíbe.
6. Para cada resultado, guardar documento, ID, commit, tags que motivaram a recuperação e trecho de evidência. Aplicar os filtros atuais de histórico e natureza documental; nunca excluir um artigo inteiro por `revogado` agregado.
7. Uma busca sem candidatos deve registrar a lacuna. Pode-se ampliar para ancestrais pertinentes, mantendo o registro das tags; texto e embeddings podem reordenar resultados, mas não substituir silenciosamente o filtro obrigatório.

Exemplo: `tema=esgoto-sanitario`, `instrumento=padrao-lancamento`, termo `DBO` deve recuperar art. 21, I, d, da CONAMA 430 e seu caput. O agente deve ler as alternativas e exceções (120 mg/L, remoção mínima ou estudo de autodepuração), sem transformar o primeiro número em limite incondicional. No caso de lixiviado recebido por ETE, recuperar também art. 21, § 2º.

## Critério para a próxima redução

Para cada ocorrência, registrar ação manter/remover/substituir, ID, trecho de evidência, motivo e consulta de aceitação. Remover apenas quando houver duplicata real, atribuição incorreta ou informação migrada para outra faceta consultável. Priorizar regras de licenciamento e anexos repetidos, mas não herdar tags entre atividades apenas por texto semelhante. Separar rastreabilidade editorial da taxonomia temática. Evitar um teto arbitrário por dispositivo.

A próxima revisão semântica deve cobrir primeiro Decreto PR 9.541/2025, Lei PR 22.252/2024 e Lei 15.190/2025, depois normas setoriais e seus anexos, recursos hídricos, resíduos, ar, vegetação, radioproteção e segurança do trabalho. A fila integral permanece no inventário. A árvore proposta não equivale à validação de cada atribuição existente.

## Integridade e validação

O texto fora das tags foi comparado com o snapshot; os IDs, wikilinks e tags de controle foram preservados. O validador da base retornou zero erros e 153 avisos de referências fora do acervo. O HTML foi regenerado (o gerador não exibe tags, portanto não produziu diferença versionada). O validador taxonômico cobre todo o vocabulário, verifica pais, ciclos e aliases; seus testes incluem rejeição de estruturas inválidas. Resultados adicionais estão em `validacao.md`.

Não foram inferidas revogações tácitas nem alteradas remissões. A regra de transição do art. 29 deve ser lida com sua data-base; a tag não a torna um prazo aberto para novos empreendimentos. O trabalho local não altera a publicação no GitHub.
