# API de consulta e assistente — Cloudflare Workers AI

## Rotas

- `GET /`: versão e rotas.
- `GET /health`: manifesto publicado, AI e configuração do chat.
- `POST /api/legislacao/candidatos`: busca lexical por eixos, sem inferência.
- `POST /api/legislacao/analisar`: análise por IA para integração entre servidores. Continua exigindo `Authorization: Bearer <ANALYZE_TOKEN>`.
- `POST /api/legislacao/chat`: consulta pública do assistente, sem expor tokens de backend.

O site oferece o assistente em `assistente.html`, com acesso destacado na página inicial. A busca livre e a análise lexical continuam em `index.html`.

### Entrada

```json
{
  "campos": {
    "atividade": "Atividade médica ambulatorial com exames complementares",
    "modalidade": "renovacao licenca operacao",
    "agua": "rede",
    "efluentes": "lancamento rede coletora esgoto",
    "residuos": "residuos servico saude"
  },
  "cnaes": ["8630-5/02"],
  "pergunta": "Quais dispositivos preciso conferir para renovar a LO?",
  "historico": ["Quais normas tratam deste caso?"]
}
```

`pergunta` (3 a 1.200 caracteres) e `historico` (até quatro perguntas anteriores) são usados apenas em `/chat`. Atividade é obrigatória. Os campos atuais descrevem o caso; o histórico não é fonte normativa e não substitui os campos. As respostas antigas da IA nunca são aceitas como evidência pelo servidor.

## Recuperação e fundamentação

1. Confere commit e hashes SHA-256 dos arquivos do mesmo manifesto.
2. Busca normas por atividade/CNAE, modalidade, efluentes, resíduos e demais eixos informados; `/chat` acrescenta a pergunta atual.
3. Baixa fatias das normas selecionadas, quatro por vez. Não baixa os índices integrais de dispositivos e grafo.
4. Reserva evidências por eixo, diversifica famílias de normas e não usa pontuações de eixos diferentes como se fossem comparáveis.
5. Acrescenta pais, caput, âmbito, ressalvas e remissões existentes na fatia. Exclui rótulos sem texto substantivo. Marca textos cortados.
6. Envia o pacote ao `@cf/openai/gpt-oss-120b` via Workers AI, usando `input`, `reasoning` e `max_output_tokens` da Responses API. Não configura ferramentas de web ou execução.
7. Lê somente `output_text` de mensagens finais. Não publica raciocínio interno. Aceita também o formato legado `response` para testes/compatibilidade.
8. Confere cada ID e cada citação literal. Monta URLs e linhas a partir da fonte. Descarta campos extras. Um item inválido é omitido com lacuna explícita; se nenhum item for verificável, devolve fontes candidatas, sem conclusão da IA.

O contrato permanece `consulta-hibrida/1`, com `itens`, `lacunas` e `commit`. Cada item pode trazer `verificar`, `eixo`, `texto_parcial` e fontes de cada evidência. Estados: `analisado`, `sem_evidencias`, `fontes_para_conferencia`.

## Segurança, limites e privacidade

- `ANALYZE_TOKEN` continua como Secret **somente no backend**. Nunca inserir no site, na URL, no GitHub ou no localStorage.
- `/chat` é público, não autentica pessoas. Origin permitido e CORS não são autenticação.
- `CHAT_RATE_LIMIT`: 4 tentativas/minuto/IP em cada localidade Cloudflare. O IP é lido de `CF-Connecting-IP`, sem aceitar `X-Forwarded-For` fornecido pelo cliente.
- `ChatBudget`: objeto SQLite com contador global atômico, máximo de **80 reservas de inferência por dia UTC**, inclusive tentativas cujo modelo falhe. Não há repetição automática de inferência. Reinício às 21h em Brasília (UTC−3).
- O objeto global coordena somente a reserva de consumo; não executa busca ou IA, nem armazena perguntas, respostas ou IPs. A reserva não é um teto monetário de toda a conta: `/analisar`, CPU, armazenamento e outros serviços são separados.
- Sem `PUBLIC_CHAT=true`, limite por IP ou orçamento, a rota pública falha fechada. Para desativar, altere `PUBLIC_CHAT` no Wrangler e publique.
- Limites públicos podem ser consumidos por terceiros. Para uso privado/múltiplos clientes, adicionar autenticação por usuário/Cloudflare Access e orçamento por usuário.
- Corpo lido com limite real de 16 KB, mesmo sem Content-Length. Fontes têm limites de tamanho e timeout. Saída não é HTML e a interface usa `textContent`.
- Conversa e dados ficam em memória da aba. Exportação é voluntária para a área de transferência. Logs da aplicação registram rota/tipo de falha, sem texto do caso ou segredo. Os dados são processados pelo Cloudflare ao consultar.

## Implantação

O workflow existente `implantar-worker.yml` publica depois de `site de busca` concluir no `main`. O PR precisa ser mesclado para essa sequência ocorrer.

Segredos existentes no GitHub: `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID`, da conta correta. O Secret `ANALYZE_TOKEN` existente no Worker é preservado pelo Wrangler.

`wrangler.jsonc` acrescenta binding de rate limit, Durable Object SQLite e migração `chat-budget-v1`. Não implantar o código avulso no editor do painel. Para builds manuais a partir da raiz:

```sh
npx wrangler@4 deploy --dry-run --config cloudflare/legislacao-ambiental-api/wrangler.jsonc
npx wrangler@4 deploy --config cloudflare/legislacao-ambiental-api/wrangler.jsonc
```

Depois da publicação: conferir `/health` com `chat:true` e abrir o assistente pelo domínio GitHub Pages permitido. Confirmar uma pergunta real. O endereço remoto existente e o deploy anterior não comprovam que um PR novo esteja no ar.

## Testes reproduzíveis

```sh
python scripts/validar.py
python -m unittest discover -s testes -v
python scripts/gerar_site.py _site
python scripts/validar_indices.py _site
node --test testes/motor.test.mjs testes/worker-contract.test.mjs
SITE_DIR=_site node --test testes/worker-integracao.test.mjs
node --test testes/worker-memoria.test.mjs
node scripts/auditar_assistente.mjs
```

O teste de integração cobre análise autenticada, chat, recuperação por eixos, fallback por resposta inválida e orçamento esgotado, com acervo real e IA simulada. `scripts/auditar_assistente.mjs /tmp/payload.json` pode gerar o pedido exato para uma avaliação real opcional; não usa credenciais nem chama IA por conta própria.

Interface: com Playwright instalado e `_site` servido na porta 8765, `node testes/assistente-ui.cjs`. `UI_BASE_URL` e `CHROMIUM_EXECUTABLE` são opcionais. O teste simula respostas da API e não consome IA.

## Limitações

- Recuperação lexical por eixos + grafo + LLM; **não é busca vetorial**. Texto muito diferente do vocabulário da base ainda pode não recuperar o dispositivo correto.
- O pacote possui até 12 principais e 40 dispositivos totais; remissões são limitadas às que a fatia contém. Pode haver ressalvas não recuperadas.
- Citação literal válida não prova que a interpretação, vigência ou hierarquia jurídica esteja correta. Não usar a classificação automática como parecer definitivo.
- Os dados não informados continuam lacunas; o sistema não deve inventar porte, modalidade automática, destinação ou condições de operação.
- A memória medida localmente não é garantia de pico/concor­rência no runtime Cloudflare. Monitorar erros de recursos em produção.
- Testes com modelo real são amostrais, não uma certificação de precisão jurídica.
