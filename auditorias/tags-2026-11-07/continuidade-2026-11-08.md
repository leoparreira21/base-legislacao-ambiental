# Revisão semântica e integração — 08/11/2026

## Estado real da entrega

Este lote continua o PR #60 e **não conclui a revisão integral do acervo**. Há leitura registrada de 50 dos 107 anexos técnicos, da Lei PR 22.252/2024 e do Decreto PR 12.799/2026, além do piloto anterior da CONAMA 430/2011. Outros sete dispositivos de cinco anexos receberam revisão dirigida. O inventário distingue esses estados; uma revisão dirigida não significa leitura integral do documento.

Os subagentes interrompidos por limite de uso deixaram os resultados gravados. Foram integrados somente os relatórios existentes, conferidos contra os arquivos atuais; leituras apenas anunciadas em mensagens não foram contadas como concluídas. Permanecem sem cobertura integral registrada 72 normas, 57 anexos e o comentário oficial. A redução substancial do vocabulário solicitada ainda depende dessa revisão.

## Alterações e métricas

Comparação desta etapa com `88429355072d0661d344d1ae5ba1aa00d0e2e437`:

| Métrica | Resultado |
|---|---:|
| Arquivos normativos/anexos modificados | 52 |
| Decisões integradas, incluindo manutenção e frontmatter | 1.364 |
| Decisões com alteração de tags diretas/agregadas | 392 |
| Decisões de sincronização de frontmatter | 15 |
| Ocorrências removidas | 105 |
| Ocorrências acrescentadas, com tags já existentes | 400 |
| Saldo de ocorrências | +295 |
| Vocabulário distinto | 819 → 819 |
| Ocorrências no corpo | 39.843 → 40.138 |

**Não houve redução líquida neste lote.** Vários anexos tinham tags somente no frontmatter; os requisitos não tinham indexação direta. Os acréscimos corrigem lacunas de recuperação, usando conceitos existentes. Nenhum conceito novo foi criado. Os números são contagens de anotações, não indicadores de qualidade jurídica nem de precisão de um agente de IA.

Exemplos verificados:

- Lei PR 22.252/2024, art. 22: `pendencia-judicial` torna explícito o gatilho da eventual suspensão do processo; art. 40 passa a representar a definição de estudos ambientais e termos de referência, em vez de apenas porte e potencial poluidor.
- Decreto PR 12.799/2026, art. 5: inclusão de `revogacao` para o ato revogador, sem classificá-lo como `revogado`.
- INs IAT 30 e 31/2025, anexo V, cabeçalhos de relatórios: `residuo-transporte` foi trocada por `transporte`. Trata-se da operação de transportar resíduos, não da categoria de resíduos originados de serviços de transporte.
- IN IAT 32/2025, anexo IV, linha 74: levantamento de vestígios culturais conserva `bem-cultural`; retirada de `iphan`, pois o item não exige manifestação desse órgão.
- Anexos de estudos: descrição ou medição de distância não equivale a estabelecer um afastamento mínimo; essas ocorrências foram corrigidas nos lotes documentados.

## Uso do Graphify e economia de contexto

O plugin Graphify foi consultado. `graph_stats` e `recall` informaram ausência de workspace selecionado; `list_workspaces` retornou `[]`. Assim, **nenhum dado foi consultado no índice nem salvo na memória remota do Graphify**. Para usar o serviço conectado, é necessário disponibilizar um workspace autorizado que contenha este repositório.

Foi preparado um grafo local no formato de extração usado pela integração Graphify já presente no projeto:

```sh
python scripts/integrar_revisao_tags.py
```

Saídas:

- `graphify-out/revisao-tags.graphify.json`: nós de documentos, dispositivos, decisões e tags; arestas de pertença, decisão, tag direta e identidade textual. Artefato gerado, ignorado pelo Git como o restante de `graphify-out/`; reconstruível com o comando acima.
- `auditorias/tags-2026-11-07/integracao-manifesto.json`: cobertura declarada, hashes SHA-256 dos arquivos lidos, limites e divergências.
- `auditorias/tags-2026-11-07/integracao-repeticoes.json`: 80 grupos de texto normalizado idêntico, com 139 ocorrências adicionais a conferir e links lógicos às decisões existentes.

Consultas curtas evitam carregar a base inteira no contexto do agente:

```sh
python scripts/integrar_revisao_tags.py --tag transporte --limite 5
python scripts/integrar_revisao_tags.py --arquivo lei-estadual-22252 --limite 5
```

O script usa o parser de dispositivos existente. O processamento do corpus é local e determinístico, sem chamadas a LLM. Não foi medido um percentual de economia de tokens. Números e destinos das remissões são preservados ao formar grupos: textos com limites ou referências diferentes não são tratados como idênticos. **Identidade textual não autoriza reaplicar uma decisão sem conferir atividade, modalidade, norma-mãe, contexto e situação do texto.**

## Questões jurídicas preservadas

As remissões problemáticas já anotadas na Lei PR 22.252/2024 foram preservadas (arts. 27, 31, 39 e 47). Não foram corrigidas por inferência. O Decreto 12.799/2026 distingue as hipóteses dos §§ 2º e 3º do art. 56 do Decreto 9.541/2025; essa distinção permanece.

Os anexos da CONAMA 411/2009 trazem limitações de compilação diante das alterações de 2016/2018 e aviso de revogação no anexo V. A revisão de tags não corrige essa situação nem certifica que o texto esteja atualmente aplicável. A vigência externa e a atualização do texto dependem de trabalho próprio, com fonte oficial. Anexos de norma-mãe revogada continuam sendo material histórico.

## Verificações

O integrador rejeita decisão cujo ID não exista ou cujo resultado não corresponda às tags atuais, além de decisões conflitantes. A comparação dos 52 arquivos modificados preservou texto fora das tags, IDs, wikilinks e marcadores de controle. O validador da base e o da taxonomia passaram. A validação de índices encontrou zero erros. As saídas completas de testes e auditoria estão resumidas em `validacao-semantica.md`.

A taxonomia proposta continua sem ativação no motor atual. As arestas de identidade textual são auxílio de revisão, não relações de aplicabilidade jurídica ou herança temática.
