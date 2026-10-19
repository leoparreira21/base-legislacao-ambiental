# API híbrida — Cloudflare Workers AI

Código-fonte do Worker `legislacao-ambiental-api` implantado na conta Cloudflare.

## Endpoints

- `GET /`: metadados, versão e rotas.
- `GET /health`: disponibilidade do manifesto e índices.
- `POST /api/legislacao/candidatos`: análise lexical por eixos usando o motor real de `site/motor.js`, sem chamada à IA.
- `POST /api/legislacao/analisar`: recuperação híbrida e chamada a `env.AI.run`; requer segredo `ANALYZE_TOKEN`.

Entrada JSON, exemplo:

```json
{
  "campos": {
    "atividade": "Atividade médica ambulatorial com exames complementares",
    "modalidade": "renovacao licenca operacao",
    "agua": "rede",
    "efluentes": "lancamento rede coletora esgoto",
    "residuos": "residuos servico saude"
  },
  "cnaes": ["8630-5/02"]
}
```

O mecanismo carrega manifesto e índices do **mesmo commit**, confere hashes SHA256
e seleciona dispositivos por evidência, hierarquia e remissões explícitas.

Na rota com IA, o Worker não baixa `dispositivos.json` (~29 MB) nem `grafo.json`
(~7 MB): baixa só `fatias/<norma>.json` das normas que o motor selecionou (até 6 por
eixo, 4 downloads por vez), cada uma com hash no `manifesto.json`. A fatia, gerada por
`scripts/gerar_site.py`, traz os dispositivos elegíveis da norma, as três primeiras
remissões de cada um (filtradas como antes) e a cópia dos destinos que estão em outras
normas. Uma fatia por norma, e não duas (dispositivos e grafo), porque os casos de
auditoria selecionam até 26 normas e o plano Free do Workers admite 50 subrequisições.
A versão do contrato (`consulta-hibrida/1`) é imposta pelo servidor; commits divergentes são rejeitados. A resposta do modelo é aceita somente se os IDs existem no pacote recebido
e as citações são substrings literais da fonte. Isso **não** prova correção jurídica.

## Segurança e autorização

**Antes de usar a rota com IA, crie um Secret** no painel Cloudflare:
Workers & Pages > legislacao-ambiental-api > Settings > Variables and Secrets
> Add > Secret. Nome: `ANALYZE_TOKEN`; valor: token aleatório longo,
gerado em ambiente privado. Esse segredo **nunca** deve estar no código, no
GitHub, no navegador nem em variáveis públicas de frontend.

O servidor que chama a API deve enviar:
`Authorization: Bearer <token>`.

O token deve ser armazenado também como segredo **do backend chamador**,
jamais no React, HTML, JavaScript cliente ou em URL. Além de autenticação,
configurar limites de requisições, controles de custo e observabilidade
antes de permitir uso de terceiros.

Não há cobrança pela chamada lexical; Workers AI utiliza a franquia da conta
e pode gerar cobrança conforme o plano e volume.

## Implantação por código-fonte

A partir da raiz do repositório, executar:

```sh
npx wrangler deploy --config cloudflare/legislacao-ambiental-api/wrangler.jsonc
```

A importação `../../site/motor.js` permite que Wrangler inclua o mesmo
motor usado pelo site. O Worker atual foi implantado via API com
`worker.mjs` + `motor.mjs`, que tem o mesmo conteúdo de `site/motor.js`.

## Limitações atuais

- O pacote de recuperação é limitado a ~20 evidências e considera a
  primeira camada das remissões do grafo, não substituindo análise humana.
- Cada requisição ainda monta o motor de busca a partir de `index.json` e
  `cnae.json`: ~95 MB de memória viva e a maior parte da CPU, nas duas rotas.
  É o próximo ponto a reduzir se o limite de 128 MB apertar.
- Se o modelo retornar texto não conforme ou citações inexistentes,
  responde com erro 503 (não publica fundamentação inválida).
- `CORS` é restrito aos domínios conhecidos, mas **não** autentica
  chamadas por si só.
- A análise pública exige um servidor intermediário autenticado do
  IAT Report Builder; não chamar diretamente da página pública com segredo.

## Testes

```sh
node --check cloudflare/legislacao-ambiental-api/worker.mjs
node --test testes/worker-contract.test.mjs testes/worker-smoke.test.mjs
```

Os testes de smoke dependem da API implantada e de conectividade.
Não incluem a rota de IA paga nem expõem tokens de terceiros.

Memória da rota `/analisar`, sem rede e sem IA (fetch e `env.AI` simulados sobre o
site gerado; falha acima de 110 MB, de 50 subrequisições ou se passar o motor em
mais de 15 MB):

```sh
python scripts/gerar_site.py _site
node --test testes/worker-memoria.test.mjs
```
