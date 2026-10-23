# Contrato de interação

| Capacidade | Dono canônico | Regra e fonte |
|---|---|---|
| Opções dos dados do caso | site/motor.js OPCOES_CASO | Mesmas opções na busca e no assistente; localização não informada não presume manancial |
| Controles e tokens | site/estilo.css | Reutilizados da busca; selects nativos; botões sem substitutos não semânticos |
| Envio e cancelamento | site/assistente.js | Uma requisição por vez, timeout de 180 s, preservação de pergunta, descarte de resposta atrasada |
| Referências normativas | worker.mjs checkAI | Somente IDs recuperados, citações literais, fontes montadas pelo servidor |
| Privacidade | pedido do usuário + README da API | Sem armazenar perguntas em logs, URL ou armazenamento persistente; envio ao Cloudflare ao consultar |
| Consumo público | wrangler.jsonc + orcamento.mjs | 4 chamadas por minuto/IP/localidade, 80 reservas de inferência/dia UTC global; falha fechada sem bindings |
| Integrações privadas | README da API | /analisar continua exigindo Bearer; nenhum segredo no frontend |
| Novo caso | site/assistente.js | Limpar só esta aba; uma restauração disponível até próxima troca |
| Exportação | site/assistente.js | Copiar texto com fatos, IDs, citações, fontes, commit e lacunas |

Não há login, exclusão remota nem armazenamento de conversas. O chatbot público não autentica usuários; CORS não é autenticação. Dados anteriores no histórico são apenas perguntas, nunca fonte normativa. Os campos atuais prevalecem; conflitos devem ser sinalizados. Respostas sem evidência válida mostram candidatos para conferência, não parecer fabricado.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Select/Listbox | Native select | site/motor.js OPCOES_CASO | Popup do sistema operacional | testes/assistente-ui.cjs |
| Button | .btn / .more | site/estilo.css | Primário, secundário e link | testes/assistente-ui.cjs |
| Textarea | .resize-none | site/estilo.css e assistente.js fit | Crescimento até 300px no chat | testes/assistente-ui.cjs |
| Async query | assistente.js | Contrato da API | Cancelar, tentar novamente | testes/worker-contract.test.mjs |
| Consulta complementar | site/complementar.js | Candidatos separados da base curada, fonte ctresb-leis identificada, falha recuperável sem impedir consulta principal; regras em docs/integracao-ctresb.md |
