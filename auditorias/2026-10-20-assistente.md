# Auditoria do assistente — 20/10/2026

Base examinada: `a69904349ad26500953df709c834f5e7f7f84b93`. Escopo: código, seleção de evidências, contratos, configuração Cloudflare e interface. Nenhum texto de norma foi alterado e não houve consulta externa para suprir legislação ausente.

## Achados e tratamento

| Prioridade | Evidência | Tratamento |
|---|---|---|
| Alta | No caso de ambulatório, o pacote anterior era dominado por modalidade, sem principais de efluentes ou resíduos | Reserva por eixo, diversidade de famílias normativas e pergunta específica |
| Alta | Citações válidas não garantem aplicabilidade; rótulo “Licença de Operação” era selecionado como principal | Excluir rótulos curtos sem conteúdo; incluir pais, caput e âmbito; explicitar limites |
| Alta | Texto principal cortado em 1.200 caracteres e contexto em 550, sem sinalização | Até 2.500 por dispositivo, orçamento total, indicador de corte e classificação condicionada |
| Alta | Modelo Llama produziu strings no lugar de objetos de evidência, alterou acentos e retornou pontuação repetida em uma chamada | Teste real comparativo; migração para GPT-OSS 120B, Responses API; validação independente continua obrigatória |
| Alta | Não havia acesso seguro da página estática à rota privada de IA | Nova rota pública, sem segredo, limitada por IP e contador global atômico; rota privada preservada |
| Média | `lacunas` e campos extras não eram plenamente validados | Allowlist, limites e validação dos tipos, fontes montadas pelo servidor |
| Média | Uma citação inválida descartava toda a resposta | Validação por item, lacuna explícita e fallback para fontes quando nenhum item passa |
| Média | O Worker montava o índice completo de sugestão CNAE sem utilizá-lo | Opção para omitir Sets da triagem no Worker, mantendo expansão por códigos e a triagem no site |
| Média | Corpo era limitado só depois da leitura | Leitura incremental com limite real e timeouts nas fontes |
| Média | Estilo `.panel` podia sobrepor `hidden`; ausência de viewport móvel | Regra `[hidden]`, viewport, teclado nas abas e estilos compartilhados |

## Acervo e alcance

174 documentos: 67 normas, 106 anexos e um comentário; 40.754 dispositivos, 39.486 relações e 3.438 pendências no grafo. Validador da base: zero erros e 146 avisos, sobretudo referências fora do acervo. Esses avisos são preexistentes. A existência de 40 mil dispositivos não equivale a cobertura completa nem a 40 mil dispositivos vigentes/elegíveis.

O novo pacote do caso de ambulatório inclui principais nos eixos atividade, modalidade, efluentes e resíduos, além do art. 1º, parágrafo único, da CONAMA 430 como contexto para lançamento indireto. Água de rede mantém a nota sem presumir captação própria. O procedimento reproduzível é `node scripts/auditar_assistente.mjs`.

## Avaliação real de IA

Foram feitas quatro chamadas reais pelo conector Cloudflare: três ao Llama e uma ao GPT-OSS 120B, usando o pacote recuperado do acervo. Não são testes do endpoint novo publicado. As saídas do Llama falharam na conferência de formato/texto; o GPT-OSS gerou oito itens, sete com citações literais verificáveis e um descartável por divergência de texto.

Isso NÃO significa 87,5% de precisão jurídica: mede apenas a conferência de citações nessa amostra. A leitura manual ainda observou formulações excessivas (possibilidade tratada como obrigação, condição tratada como exclusiva); o prompt foi reforçado, mas não há prova automática de correção semântica. As sugestões precisam de revisão humana.

## Verificação

- 28 testes Python aprovados; validador da base com zero erros.
- Contratos Node: 16 testes aprovados, incluindo entrada, truncamento, allowlist, orçamento, Responses API e descartes parciais.
- Motor: 11 testes aprovados.
- Integração: acervo real, IA simulada, chat, fallback e limite diário.
- Memória: 25 testes (motor + 24 casos), dentro dos tetos de memória e subrequisições; medição local, não runtime de produção.
- Interface em Chromium/Playwright: desktop e 390px, validação, sucesso, fontes, conteúdo HTML tratado como texto, erro 429, cancelamento, descarte de resposta atrasada, novo caso/restauração e abas por teclado aprovados, com API simulada.
- Wrangler 4: bundle e configuração validados em `deploy --dry-run`.
- Auditor estático de UI executado em modo strict: propriedade dos selects e resize resolvidos. Os 11 avisos restantes são falsos positivos de botões ligados por módulos JavaScript, pois o auditor reconhece apenas handlers inline. Não foram adicionados handlers fictícios para silenciar o auditor.

## Publicação e riscos remanescentes

As alterações são entregues em PR. O workflow existente publica o Pages e, em seguida, o Worker depois do merge. Até isso ocorrer, não considerar o novo assistente disponível em produção. A migração cria um Durable Object SQLite para orçamento. A busca livre permanece disponível se a IA estiver indisponível.

CORS não autentica usuários. O chat público tem teto diário compartilhado, que terceiros podem consumir; a rota autenticada não usa esse teto. O contador limita reservas de inferência, não toda a fatura Cloudflare. Recuperação continua lexical com expansão pelo grafo, sem embeddings ou validação externa de vigência.
