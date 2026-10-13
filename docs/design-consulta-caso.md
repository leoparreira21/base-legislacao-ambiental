# Desenho: API de consulta de caso (busca-caso/1)

Status: **proposta, aguardando aprovação**. Nenhum código foi escrito.

Objetivo: o botão de sugestões de legislação no rascunho (iatreports.online) abre uma janela com o formulário de caso já preenchido pelo relatório. Os resultados são os mesmos da aba "Análise de caso" do site de busca e vêm de um endpoint JSON.

Repositórios: backend = `base-legislacao-ambiental` (acervo + site no GitHub Pages); frontend = `iat-report-scribe` (Lovable, TanStack Start no Cloudflare).

## Decisões tomadas com o usuário

1. **Hospedagem:** o endpoint roda no servidor do frontend. O GitHub Pages não executa código. O backend publica no Pages o motor de busca, um manifesto e um índice pré-computado.
2. **Mapeamento:** a janela abre com o formulário pré-preenchido a partir do relatório. O usuário pode ajustar os campos antes de consultar.
3. **Painel atual:** o painel da seção 3 (agente n8n, API Consulta Ambiental, gateway de IA do Lovable) é substituído. O código antigo sai numa etapa posterior.

## 1. Contexto

Chamada síncrona de leitura (RPC "consultar caso"), exposta como rota de servidor TanStack Start no runtime Cloudflare do frontend. Não é CRUD.

- Carga: pequena (poucos usuários, menos de 1 req/s).
- Gargalo: materializar o acervo (cerca de 9 MB, 9.140 trechos) numa isolate fria, não o throughput.
- Execução: cada consulta roda o motor de forma síncrona (CPU pura, sem I/O) sobre um snapshot imutável por commit.
- Falha: servir a última cópia boa e avisar.
- Concorrência: single-flight na carga do snapshot; consultas independentes e sem estado.

```
BACKEND (CI -> Pages)                 FRONTEND (Cloudflare)                       NAVEGADOR
site/motor/*.js (fonte única) --sync-> src/vendor/legislacao/ (cópia versionada)  mapeamento vendorizado
manifest.json (hashes, versões)  ---> acervo.server.ts (single-flight, hash)  --> pré-preenche o diálogo
indice-f1.json (pré-tokenizado) ----> POST /api/legislacao/caso -> JSON busca-caso/1 -> renderiza JSON
cnae/sinonimos/ambitos/caso.json ---> GET  /api/legislacao/saude                     (sem HTML do servidor)
site/index.html: usa o MESMO motor e renderiza o MESMO JSON de resultado
```

Decisão estrutural: o `site/index.html` passa a renderizar a partir do mesmo `ResultadoCaso` que a API devolve. Hoje `rodarCaso()` (index.html:577-593) gera HTML direto de `buscar()`. Com a mudança, "mesmo resultado do site" vale por construção e deixa de depender só de teste.

## 2. Modelo de dados

### Artefatos

Não há tabelas. Os artefatos são imutáveis por commit e publicados no Pages:

- `index.json` (hoje gerado em `gerar_site.py:78`)
- `indice-f1.json` (novo, pré-tokenizado)
- `cnae.json`, `sinonimos.json`, `ambitos.json`
- `caso.json` (novo, esquema do formulário) e `caso-vocabulario.json` (novo)
- `motor/*.js`
- `manifest.json`

### Invariantes

Garantidas pelo código, não por schema SQL:

- **Determinismo.** Mesma entrada normalizada, mesmo commit e mesma versão do motor dão a mesma subárvore `resultado`. Metadados voláteis (`consultadoEm`, `duracaoMs`) ficam em `meta`, fora da garantia. Scores são arredondados a 4 casas.
- **Um commit por resposta.** Todos os arquivos de uma resposta vêm do mesmo commit, verificado pelo sha256 do manifesto.
- **Sem revogadas.** Norma revogada fica fora (herdado de `consultar.carregar`, `consultar.py:56`). Texto tachado já sai em `texto_atual`.
- **Formato explícito.** As tuplas posicionais dos blocos `[norma,l1,l2,id,ctx,tags,txt,k]` (`gerar_site.py:77`) passam a ter `formato` declarado.

### Mudanças nos artefatos

1. `index.json` ganha a chave `formato: 1`. O Python mantém as tuplas e documenta as posições.
2. `scripts/gerar_indice.mjs` gera `indice-f1.json`:
   - `vocab[]` e `df[]` por termo; `N` e `AVG`.
   - Por bloco: `[normaIdx, l1, l2, id, ctx, tags, txt, k, len, tf:[[termo,cont]...], cx:[termo...], tg:[termo...], seq?]`. O campo `seq` só existe para `k=2`.
   - O campo `norm` fica de fora e é calculado sob demanda (só serve a frases entre aspas, index.html:254).
   - Os conjuntos de tokens do CNAE vão pré-computados (`prepararCnae`, index.html:362).
3. `manifest.json`, com os campos da tabela abaixo.
4. `consultas/caso.json` (esquema) e `consultas/caso-vocabulario.json`.

| Campo do manifesto | Conteúdo |
|---|---|
| `commit`, `geradoEm` | commit do acervo e data de geração |
| `indices` | `{ "1": {arquivo, sha256, bytes} }`. Várias versões podem coexistir durante uma transição. |
| `arquivos` | `{nome: {sha256, bytes}}` de cnae, sinonimos, ambitos, caso, caso-vocabulario e motor/* |
| `motor` | `{versao: "1.0.0", tokenizador: "<hash de STOP+normalizar+radical>"}` |
| `contratos` | `["busca-caso/1"]` |
| `conformidade` | arquivos do mini-acervo e dos goldens (o frontend vendoriza) |

### Consultas implícitas

- `GET manifest`: revalidado a cada 5 min.
- `GET indice-f1.json`: só quando o commit muda.
- Varredura linear de ~9 mil blocos por eixo. O custo cresce linearmente com o acervo (ver risco R2).

### 2.1 Esquema do caso (`consultas/caso.json`)

Hoje os valores dos `<select>` do site são strings de consulta (por exemplo `'outorga poco agua subterranea'`, index.html:134). Isso amarraria a API a rótulos de formulário. Proposta: o contrato usa códigos estáveis (slugs), e o esquema faz a ponte entre código e consulta.

Estrutura do esquema:

- `campos[]`: `{id, rotulo, tipo: "opcao"|"texto", opcoes:[{codigo, rotulo, consulta}], max}`
- `eixos[]` (declarativo): `{id, titulo, descricao, descricaoSemValor, campo, consultaPadrao, usaAtividade, listasCnae, ignorarQuando:[codigo], nota:{quando:{agua:"rede"}, texto}}`
- `textos`: mensagens canônicas de lacuna e de nota (hoje fixas em index.html:556 e 588)

O esquema reproduz as regras de `eixos()` (index.html:565-576):

- O eixo Atividade só existe se houver atividade.
- Localização `-` é pulada.
- Água `rede` gera nota e não faz busca.

Mudar uma opção, uma consulta ou um eixo passa a ser editar JSON. Os dois lados leem o mesmo arquivo. O motor expõe `montarEixos(entrada, esquema)`.

| Campo | Códigos |
|---|---|
| modalidade | `nao-informado`, `lp`, `li`, `lo`, `rlo`, `las`, `rlas` (novo), `lac`, `ampliacao`, `regularizacao`, `dispensa` |
| agua | `nao-informado`, `rede`, `poco`, `captacao-superficial` |
| efluentes | `nao-informado`, `rede-coletora`, `corpo-hidrico`, `solo`, `galeria-pluvial` |
| localizacao | `triagem` (o "Não informado" do site, que consulta `'manancial area protegida'`), `manancial`, `karst`, `app`, `uc`, `sem-restricao` |

### 2.2 Requisição: `POST /api/legislacao/caso`

JSON, no máximo 16 KB, validação zod `.strict()`.

| Campo | Regra |
|---|---|
| `contrato` | `"busca-caso/1"`, obrigatório |
| `atividade` | texto, até 300 caracteres |
| `cnaes` | opcional, até 10 códigos de 7 dígitos. Ausente: o servidor faz a triagem automática pela atividade e só marca o candidato inequívoco (como o site, index.html:397). Presente: usa exatamente esses códigos; lista vazia significa nenhum. |
| `modalidade`, `agua`, `efluentes`, `localizacao` | código do esquema; o servidor valida contra o `caso.json` vendorizado |
| `residuos`, `outros` | texto, até 400 caracteres |
| `filtros` | `{esfera: "" \| "federal" \| "estadual", anexos: bool, listas: bool}` |
| `limites` | `{normasPorEixo ≤ 20 (padrão 10), trechosPorNorma ≤ 12 (padrão 6)}` |

O contrato é uma lista fechada de campos técnicos. CPF, CNPJ, nomes e relatos brutos não têm campo e nunca trafegam. Nos textos livres, padrões de CPF e CNPJ são trocados por `[omitido]` e geram um aviso.

### 2.3 Resposta (200)

| Chave | Conteúdo |
|---|---|
| `contrato` | `"busca-caso/1"` |
| `meta` | `{requestId, consultadoEm, duracaoMs, cache: "hit" \| "miss"}` (fora da garantia de determinismo) |
| `acervo` | `{commit, formato, geradoEm, idadeSegundos, copiaAnterior: bool}` |
| `motor` | `{versao, defasado: bool}` |
| `entrada` | a entrada normalizada que de fato foi usada |
| `cnae` | `{origem: "informado" \| "triagem", selecionados: [{codigo, descricao}], candidatos: [{codigo, descricao, via, auto, hierarquia}]}` |
| `avisos[]` | `{codigo, texto}`, por exemplo `CNAE_DESCONHECIDO` e `DADO_PESSOAL_OMITIDO` |
| `eixos[]` | ver abaixo |

Cada item de `eixos[]` traz:

- `id`, `titulo`, `descricao`
- `consulta`: a busca efetivamente usada
- `status`: `resultados`, `lacuna` ou `nota`
- `mensagem`: presente quando o status é `lacuna` ou `nota`
- `termos`: conceitos e sinônimos usados
- `totalNormas`
- `normas[]`

Cada item de `normas[]` traz: `id`, `titulo`, `nomeExibicao`, `tipo`, `esfera`, `situacao`, `ementa`, `anexo`, `normaMae`, `motivo`, `score`, `totalTrechos` e `trechos[]`.

Cada item de `trechos[]` traz:

- `id` e `linhas: [l1, l2]`
- `contexto`
- `tipo`: `dispositivo`, `anexo` ou `lista` (de `k` = 0, 1, 2)
- `texto` e `truncado`: o texto é cortado em 1.200 caracteres; o texto completo está no link
- `url`: `…/blob/<commit>/<arquivo>#L<l1>-L<l2>` (linhas, nunca a âncora `{#id}`)
- `termosDestacados[]`: palavras como aparecem no texto, sem HTML

A seleção de trechos segue a lógica atual de `normaHTML` (index.html:459-479): no máximo 2 linhas por tabela, e `linhasResumidas` conta as ocultas. Essa lógica vai para o motor como `selecionarTrechos()`, usada pelo site e pela API.

### 2.4 Erros

Corpo de erro: `{contrato, erro: {codigo, mensagem, detalhes?, requestId}}`.

| Código | HTTP | Quando |
|---|---|---|
| `ENTRADA_INVALIDA` | 400 | JSON malformado, campo desconhecido, código fora do esquema, texto longo demais |
| `CONTRATO_NAO_SUPORTADO` | 400 | valor de `contrato` desconhecido (por exemplo, aba antiga aberta contra servidor novo) |
| `CASO_VAZIO` | 422 | sem atividade e sem CNAE |
| `LIMITE_EXCEDIDO` | 429 | excesso de requisições; vem com `Retry-After` |
| `ACERVO_INDISPONIVEL` | 503 | sem snapshot em memória e Pages inacessível |
| `ACERVO_INCOMPATIVEL` | 502 | formato, tokenizador ou versão principal do motor incompatíveis, sem cópia compatível em memória |
| `ERRO_INTERNO` | 500 | exceção não prevista; vem com `requestId` |

### 2.5 Política de versões

Três versões independentes permitem que cada lado evolua sem quebrar o outro.

**`contrato` (`busca-caso/N`)**: o fio entre navegador e servidor. Muda no frontend.
- Campo opcional novo, na entrada ou na saída, não muda N. O cliente ignora chaves desconhecidas.
- Renomear, remover ou mudar o significado de um campo cria N+1.
- O servidor aceita N e N-1 durante uma janela de deploy.

**`formato` do índice**: layout das tuplas e tokenização. Muda no backend.
- Mudou o layout ou o tokenizador, o número sobe.
- Na transição, o manifesto lista os dois formatos lado a lado (`indices: {"1", "2"}`).
- O frontend escolhe o maior formato que o motor vendorizado suporta.
- O formato antigo só sai depois que o frontend atualiza.

**`motor.versao`** (semver): comportamento de pontuação e admissão. Muda no backend.
- Versão principal (major) diferente é incompatível: o servidor mantém a cópia boa anterior ou devolve `ACERVO_INCOMPATIVEL`.
- Minor ou patch diferente é aceito, com `motor.defasado = true` (aviso discreto na UI e log `warn`).

O hash do tokenizador é uma trava de segurança. Se `radical()` mudar, o índice pré-computado fica errado sem nenhum erro aparente. Por isso o carregador exige `manifest.motor.tokenizador` igual ao vendorizado.

## 3. Modos de falha

| Falha | Detecção | O que o cliente vê | Recuperação |
|---|---|---|---|
| JSON inválido, campo extra, código fora do esquema | zod `.strict()` com o esquema vendorizado | 400 `ENTRADA_INVALIDA` | o cliente corrige o formulário |
| Sem atividade e sem CNAE | validação após normalizar | 422 `CASO_VAZIO`, erro junto ao campo | o usuário preenche |
| Corpo acima de 16 KB | leitura limitada do corpo | 413/400 | o cliente reduz |
| Excesso de requisições por IP | contador em memória (melhor esforço) | 429 com `Retry-After` | o cliente espera |
| Pages fora do ar, com snapshot em memória | timeout de 8 s por arquivo | 200 com `acervo.copiaAnterior = true` e faixa de aviso | nova tentativa em segundo plano com backoff de 15, 30 e 60 s |
| Pages fora do ar, sem snapshot (isolate fria) | timeout, com cache negativo de 15 s | 503 `ACERVO_INDISPONIVEL`, `Retry-After: 30` | o cliente oferece "Tentar de novo" |
| Deploy do Pages no meio da carga | sha256 do arquivo difere do manifesto | (transparente) | uma nova tentativa com `?t=` para furar o cache de borda; se persistir, mantém o snapshot anterior ou devolve 503 |
| Formato, tokenizador ou versão principal incompatíveis | comparação com o `versao.js` vendorizado | `copiaAnterior`; sem cópia compatível, 502 `ACERVO_INCOMPATIVEL`; `/saude` fica "degradado"; log `error` | rodar `sync:motor` (PR no frontend) |
| Índice truncado ou corrompido | hash ou `JSON.parse` falham | igual ao deploy no meio da carga | igual |
| Estouro de CPU ou memória da isolate (1101/1102) | nenhum log nosso: a Cloudflare devolve 5xx sem JSON | o cliente trata 5xx sem JSON como `ERRO_INTERNO` | limites de entrada, índice pré-computado, medição na Etapa 0, plano de shards (R2) |
| CNAE informado inexistente | consulta ao `cnae.json` | 200 com aviso `CNAE_DESCONHECIDO`; o código é ignorado | o usuário revisa |
| Cliente abortou (digitou de novo ou fechou a janela) | `request.signal` | nada; log `cancelada` | nenhuma |
| Acervo antigo (mais de 7 dias sem atualização bem-sucedida) | idade do snapshot | `acervo.antigo` em `/saude` e faixa reforçada | investigar o Pages |

Segurança:

- A URL do acervo é constante no código, sem SSRF.
- A saída é só texto, sem HTML.
- O endpoint não usa segredos.
- O `fetch` ao Pages usa `redirect: "error"`.

## 4. Autorização

- **Quem chama:** qualquer cliente. O acervo é público e a operação só lê. O endpoint não exige sessão.
  - "Quem abre o rascunho" descreve a UX, não uma garantia de acesso.
  - Hoje `queryLegislation` também não autentica (`legislation.functions.ts:5-35`). Só `analyzeLegislation` consulta `adminSession` (:58-80), e essa função sai junto com o agente.
- **Escopo:** não há multi-tenant e nenhum dado do rascunho fica no servidor. Como o contrato é uma lista fechada de campos, dado pessoal não sai por construção.
- **Onde se aplica:** na própria rota (zod strict, limites, rate limit). Sem cabeçalho CORS: a rota atende só a mesma origem.
- **Abuso de CPU:** a defesa real é uma regra de rate limiting da Cloudflare em `/api/legislacao/*`. O limitador em memória vale por isolate e só atenua (R4). Proposta: 30 consultas por minuto por IP. O limite antigo, de 5 consultas por 10 min, impede ajustar o formulário.

## 5. Idempotência e concorrência

- **Repetição:** leitura pura. Duas execuções devolvem a mesma subárvore `resultado` para o mesmo commit.
- **Consultas simultâneas:** síncronas e sem estado mutável compartilhado, então sem lock. A isolate tem uma só thread, e as consultas só se intercalam nos `await` da carga.
- **Carga do snapshot:** single-flight por uma `Promise` única. Uma atualização em andamento não bloqueia consultas (stale-while-revalidate). A troca do snapshot é atômica, por troca de referência.
- **Cache de resposta:** LRU em memória, no máximo 64 entradas e 8 MB. Chave: `sha256(entrada normalizada) + commit + motor.versao`. A última escrita vence; como o valor é determinístico, isso não causa erro.
- **Chave de idempotência:** desnecessária. O `x-request-id` serve só para correlacionar logs.
- **Cliente:** reaproveita o padrão de `use-legislation-consultation.ts`: aborta o pedido anterior, descarta resposta atrasada pelo número de sequência e aplica timeout. Acrescenta um `Map` local de resultados por assinatura da entrada, para alternar filtros sem nova chamada.

### Carregador do snapshot (`acervo.server.ts`)

1. Revalida o manifesto a cada 5 min com `fetch(..., {cf: {cacheTtl: 60}})`. O cache de borda da Cloudflare funciona como segundo nível entre isolates.
2. Se o commit mudou, baixa `indice-f1.json?v=<commit>` e os demais arquivos e confere o sha256 de cada um (`crypto.subtle`).
3. Valida a compatibilidade, hidrata (`carregarAcervo`) e troca a referência.
4. Em qualquer falha, mantém o snapshot atual e marca `copiaAnterior`.

`caches.default` não persiste em `workers.dev` e depende do domínio. Que a cópia anterior sobreviva a uma isolate fria é um bônus, não uma garantia.

## 6. Observabilidade

**Logs:** uma linha JSON por consulta, gravada no fim da requisição com `console.log`. Campos:

- `evento: "consulta_caso"`, `nivel`, `requestId`
- `contrato`, `commit`, `motor`, `formato`
- `duracaoMs` e `tempos: {carregarMs, motorMs}`
- `cache` e `snapshot` (`frio`, `fresco` ou `anterior`)
- `normasPorEixo`, `status`, `erro.codigo`
- `entradaHash`: sha256 truncado, só para correlação

Níveis: `info` no sucesso; `warn` em `copiaAnterior`, motor defasado e 429; `error` em 5xx. **Nunca** logar o texto do caso nem o IP.

**Métricas** (tiradas dos logs; não há backend de métricas):

- taxa de requisições
- erros por `erro.codigo`
- duração p50, p95 e p99, separando `frio` de `fresco`
- idade do snapshot, tempo de hidratação a frio e taxa de acerto do cache

**Healthcheck:** `GET /api/legislacao/saude` busca só o manifesto (barato) e devolve `{status: "ok" | "degradado" | "indisponivel", acervo: {commit, idadeSegundos, formato, copiaAnterior}, motor: {vendorizado, publicado, compativel}}`. Fica "degradado" com `copiaAnterior`, com motor defasado ou com acervo de mais de 7 dias.

**Trace:** o servidor usa o `x-request-id` do cliente ou o `cf-ray` e devolve o ID no cabeçalho `x-request-id` e em `meta`. A UI mostra o ID nos erros, para suporte. O `fetch` ao Pages é estático e não propaga trace.

## Mapeamento relatório → caso

**Onde fica cada parte:**

- Regras e vocabulário ficam no backend (`consultas/caso.json`, `consultas/caso-vocabulario.json`).
- A função pura `mapearRelatorio()` fica em `site/motor/mapeamento.js`. Como é vendorizada junto com o motor, uma opção de água nova e sua palavra-chave entram no mesmo PR.
- No frontend fica só o adaptador `ReportData → RelatorioNeutro` (`src/lib/consulta-caso/relatorio-para-caso.ts`), que conhece `ReportData`.
- O mapeamento roda no navegador, para pré-preencher sem ida ao servidor.
- As fontes vêm de `temasDoRelatorio(data)` (`report.ts:92`), para que temas ocultos do relatório não alimentem a consulta.

| Campo | Fonte no rascunho | Regra | Sem correspondência |
|---|---|---|---|
| `modalidade` | `tipoLicenca` | Usa o prefixo antes de " - ". `LAS`→`las`, `RLAS`→`rlas`, `LP`→`lp`, `LI`→`li`, `LO`→`lo`, `RLO`→`rlo`. `LAS-A`, `LP-A`, `LI-A`, `LO-A`→`ampliacao`. `LAS-R`, `LI-R`, `LO-R`→`regularizacao`. | `nao-informado` |
| `cnaes` | `cnaes[].texto` | Extrai `\d{7}` ou `\d{4}-\d/\d{2}`, remove repetidos, no máximo 10. A descrição que acompanha o código é ignorada. | campo omitido (aciona a triagem pela atividade) |
| `atividade` | `atividade` | Remove espaços repetidos, usa a primeira frase ou linha, corta em 300 caracteres. Se cortar, avisa na UI. | vazio |
| `agua` | `relatosTematicos.agua` | Dicionário; precedência `poco` > `captacao-superficial` > `rede` | `nao-informado` |
| `efluentes` | `efluentes` (e `drenagem`, só para `galeria-pluvial`) | Precedência `corpo-hidrico` > `solo` > `galeria-pluvial` > `rede-coletora` | `nao-informado` |
| `localizacao` | `app`, `solo`, `outros` | Precedência `karst` > `manancial` > `uc` > `app` | `triagem`. Nunca atribui `sem-restricao` sozinho. |
| `residuos` | `relatosTematicos.residuos` | Extração por vocabulário (abaixo) | vazio; o eixo usa `'gerenciamento residuo'` (index.html:572) |
| `outros` | `emissoes`, `ruidos`, `contencao`, `patios`, `veiculos`, `armazenamento` | Extração por vocabulário (abaixo) | vazio; o eixo é pulado |

**Regras comuns de detecção:**

- **Normalização:** compara tokens normalizados (sem acento, minúsculas, plural reduzido por `radical`). A comparação é por sequência de tokens, para não casar pedaços de palavras.
- **Negação:** ignora o termo quando há um negador (`nao`, `sem`, `inexistente`, `ausencia`, `nenhum`) até 4 tokens antes. Os relatórios dizem "não foi constatada APP" com frequência.
- **Sigla APP:** só conta em maiúsculas e fora de "CTF/APP".
- **Precedência:** escolhe o valor mais exigente, para não deixar norma de fora. Todos os termos encontrados aparecem em `proveniencia`, e o usuário pode trocar o valor.

**Extração de termos para `residuos` e `outros`.** A regra mantém a consulta curta e os scores comparáveis aos do site:

- O relato bruto não é enviado.
- O texto é comparado com o vocabulário controlado `caso-vocabulario.json`. Exemplos de entradas: perfurocortante, resíduos de serviços de saúde, revelador, fixador, óleo lubrificante usado, lâmpada, bateria, entulho, lodo, raio-x, ruído, caldeira, gerador, pátio de caminhão.
- Cada entrada tem um `termo` canônico e suas `variantes`.
- Ficam no máximo 6 termos, na ordem em que aparecem, unidos por ", ".
- O vocabulário começa com os exemplos do site (index.html:156 e 158) e as chaves relevantes de `sinonimos.json`.

Vantagens: resultado determinístico, nenhum dado pessoal dos relatos sai do navegador, e termos como "pátio de caminhão" admitem normas setoriais pelo âmbito (`ambitos.json`).

**Proveniência na UI:** `mapearRelatorio()` devolve `{campos, proveniencia: [{campo, valor, origem: "relatosTematicos.agua", termos: ["poço"], regra}]}`. A UI mostra etiquetas "Preenchido a partir do rascunho" com a origem de cada valor.

## Mudanças no backend (base-legislacao-ambiental)

### Arquivos

- **`site/motor/`**: módulos ESM sem DOM, numa pasta em vez de um arquivo único, para que o navegador possa importar só o mapeamento.
  - `index.js`: entrada pública.
  - `texto.js`: `normalizar`, `radical`, `tokens` (extraídos de index.html:189-205).
  - `indice.js`: `construirIndice`, `carregarAcervo`.
  - `busca.js`: `conceitos`, `pontuar`, `admite`, `buscar`.
  - `cnae.js`: `triagem`, `expansao`.
  - `caso.js`: `montarEixos`, `consultarCaso`, `selecionarTrechos`.
  - `mapeamento.js`, `esquema.js`, `versao.js`, `index.d.ts`.
- **`site/index.html`**: passa a ser `<script type="module">` e importa de `./motor/index.js`. O código de renderização fica nele, mas consome `ResultadoCaso`.
- **`scripts/gerar_indice.mjs`**: Node sem dependências npm. Lê o `_site` e escreve `indice-f1.json`.
- **`scripts/gerar_manifest.py`**: só biblioteca padrão (hashlib). Varre o `_site` e escreve `manifest.json` por último.
- **`scripts/gerar_site.py`**: acrescenta `formato` em `gerar_indice()` e copia `site/motor/*` (sem `tests/`) e os dois JSONs novos.
- **`.github/workflows/site.yml`**, entre validar e publicar:
  1. `setup-node`
  2. `node --test site/motor/tests`
  3. `python scripts/gerar_site.py _site`
  4. `node scripts/gerar_indice.mjs _site`
  5. `python scripts/gerar_manifest.py _site`
  6. Passo de orçamento: falha se `indice-f1.json` passar de 25 MB ou se o benchmark de hidratação passar do limite.
- **`.github/workflows/motor.yml`** (novo): roda os testes Node em pull requests, sem deploy.
- **`docs/motor.md`**: a política de versões da seção 2.5.
- **`consultas/caso-formulario.json`** (novo): entradas `busca-caso/1` com `esperados`. Os IDs são conferidos no texto do arquivo, nunca escritos de memória.

### Restrições operacionais

- O token da sessão na nuvem não tem escopo `workflow`: o GitHub recusa push que altere `.github/workflows/`. O conteúdo dos dois workflows é entregue ao usuário para criar pela interface.
- Não rodar `python -m unittest` no CI: `test_resultado_arquivado` já falhava antes. O controle do CI é `validar.py` mais `node --test`.
- Atualizar `CLAUDE.md`: mudança em `site/motor/`, `ambitos.json`, `sinonimos.json` ou `caso.json` exige `node --test`.
- Atualizar `licoes.md`: marcar como obsoleta a lição de 2026-10-07 sobre o n8n, depois da remoção no frontend.

## Mudanças no frontend (iat-report-scribe)

### Rotas

Seguem o padrão de `src/routes/api/drafts.ts`:

- `src/routes/api/legislacao/caso.ts`: POST
- `src/routes/api/legislacao/saude.ts`: GET

Rota com `server.handlers` em vez de `createServerFn`, porque dá:

- URL estável;
- códigos HTTP reais;
- teste com `curl`;
- reuso por outros clientes.

As server functions, ao contrário, serializam erros como mensagem solta.

### Módulos

- `src/vendor/legislacao/**`: cópia do motor, mais `VENDOR.json` com o commit de origem e os hashes.
- `scripts/sync-motor.mjs`: baixa o manifesto do Pages, baixa os arquivos listados, confere o sha256, grava em `vendor/` e escreve `VENDOR.json`. Com `--check`, só compara.
- `src/lib/consulta-caso/acervo.server.ts`: carregador do snapshot, single-flight, cache, compatibilidade.
- `src/lib/consulta-caso/limites.server.ts`: rate limit.
- `src/lib/consulta-caso/contrato.ts`: schemas zod de entrada e saída, e tipos.
- `src/lib/consulta-caso/relatorio-para-caso.ts`: adaptador de `ReportData`.
- `src/lib/consulta-caso/cliente.ts`: `fetch` com `AbortSignal` e tratamento de erro por código.
- `src/hooks/use-consulta-caso.ts`: baseado em `use-legislation-consultation.ts`. Dispensa o `localStorage` de ativação e o debounce de salvamento.
- `src/components/consulta-caso/`: `ConsultaCasoDialog.tsx`, `FormularioCaso.tsx`, `EixoResultado.tsx`, `NormaCard.tsx`, `AvisosAcervo.tsx`.
- `src/routes/relatorio.$id.tsx:1691-1702`: o `<LegislationPanel>` dá lugar a um botão que abre a janela. `addNorma` (:1037) é reaproveitado.

### UX da janela

- **Abertura:** formulário pré-preenchido, etiquetas de proveniência e primeira consulta automática. Marcar ou desmarcar CNAE e mudar filtros refazem a consulta na hora. Os demais campos refazem pelo botão "Analisar".
- **Carregando:** esqueleto por eixo, com o texto "Carregando o acervo (a primeira consulta pode demorar um pouco)".
- **Eixo com resultado:** normas com motivo de admissão, ementa e trechos com destaque. O destaque é feito por segmentos de texto, nunca por HTML.
- **Botão "Adicionar norma ao relatório":**
  - fica desabilitado se a norma já está na lista;
  - para um anexo, adiciona a norma-mãe.
- **Eixo vazio (`lacuna`):** mensagem canônica do esquema. Ela diz que a ausência na base não prova que não há norma aplicável.
- **Eixo `nota`:** texto da nota (por exemplo, rede pública sozinha não aciona outorga).
- **Acervo em cópia anterior (`copiaAnterior`):** faixa âmbar com o commit e a idade da cópia.
- **Motor defasado:** nota discreta no rodapé.
- **Erro:** mensagem por código, botão "Tentar de novo" e `requestId` copiável.
  - `CASO_VAZIO` aparece junto ao campo de atividade ou CNAE.
  - `CONTRATO_NAO_SUPORTADO` pede para recarregar a página.
- **Formulário editado depois do último resultado:** aviso "Os resultados são da consulta anterior", com botão "Analisar".
- **Rascunho mudou depois do pré-preenchimento:** aviso com botão "Reaplicar do rascunho". As edições manuais nunca são sobrescritas sem confirmação.
- **Triagem CNAE:** quando a origem é a triagem e há mais de um candidato, a janela lista os candidatos com caixas de seleção.

## Plano de testes

### Backend (`node --test site/motor/tests`)

1. **Caracterização antes da refatoração** (primeiro commit do PR B1). O script inline atual do `index.html` roda em `vm`, com um `document` falso, sobre o `index.json` real, para cerca de 25 entradas. Os resultados viram goldens, e o motor extraído precisa reproduzi-los exatamente.
2. **Unitários:** `normalizar`, `radical`, `tokens`, `admite`, `triagem`, `expansao`, `selecionarTrechos`, `montarEixos`.
3. **Mapeamento**, caso a caso:
   - negação ("não há poço");
   - sigla APP e "CTF/APP";
   - plural;
   - precedências;
   - os 13 tipos de `TIPOS_LICENCA`.
4. **Golden sobre um mini-acervo congelado**, com 3 a 4 normas, 1 anexo, 1 lista CNAE e 1 norma setorial. Um golden sobre o acervo real quebraria a cada norma nova.
5. **Equivalência de serialização:** `hidratar(JSON(construirIndice(x)))` dá o mesmo resultado que `carregarAcervo(x)`.
6. **Invariantes no acervo real (CI):**
   - determinismo;
   - nenhuma norma revogada;
   - toda `url` contém o commit;
   - nenhum texto com `~~`.
7. **Aceitação com `consultas/caso-formulario.json`:** cada ID esperado aparece em algum eixo.
8. **Cobertura de `casos-auditoria.json`:** começa como relatório informativo (ver R6).
9. **Orçamento:** tamanho do índice e tempo de hidratação.

### Frontend (`node:test`)

1. **Conformidade do vendor:** os hashes batem com `VENDOR.json`, e a suíte de conformidade vendorizada (mini-acervo + goldens) dá o mesmo resultado do backend.
2. **Carregador**, com `fetch` falso:
   - hash divergente com nova tentativa;
   - 404 e timeout;
   - formato desconhecido;
   - troca atômica do snapshot;
   - single-flight (10 chamadas simultâneas, uma carga);
   - cópia anterior.
3. **Rota:** status 400, 413, 422, 429, 502, 503 e 500 com os corpos de erro, e o cabeçalho `x-request-id`.
4. **Contrato:** os goldens de resposta validam no schema zod.
5. **Hook:** aborta o pedido anterior, descarta resposta atrasada e reaproveita resultado pela assinatura.
6. **Adaptador:** um `ReportData` de exemplo vira `RelatorioNeutro` sem nenhum campo de dado pessoal.
7. **Manual:** abrir um rascunho, conferir o preenchimento e comparar o resultado com a aba "Análise de caso" do site, para a mesma entrada.

## Sequência de construção

**Etapa 0, medição (condição para seguir; código descartável).** Carregar o `index.json` atual num Worker local (`wrangler dev` ou miniflare) e medir:

- `JSON.parse`;
- a hidratação;
- uma consulta com 7 eixos;
- o uso de memória (heap).

**Se a CPU de uma consulta fria passar do limite do plano, parar e reavaliar** (R1).

### Backend

**PR B1, extração sem mudança de comportamento:**

1. Testes de caracterização e goldens, antes de mexer no código.
2. Extrair `texto.js`, `indice.js`, `busca.js` e `cnae.js` para `site/motor/`; o `index.html` passa a importar deles.
3. Workflow `motor.yml` com `node --test` (o usuário cria o workflow pela interface).
4. Atualizar `CLAUDE.md` e `licoes.md`.

**PR B2, contrato e esquema:**

1. `consultas/caso.json` e `caso-vocabulario.json`.
2. `caso.js` (`consultarCaso()`, `ResultadoCaso`) e `mapeamento.js`.
3. A aba "Análise de caso" do `index.html` passa a renderizar a partir de `ResultadoCaso`, com o formulário gerado do esquema.
4. Mini-acervo, goldens, `caso-formulario.json` e testes de mapeamento.

**PR B3, artefatos pré-computados:**

1. `gerar_indice.mjs`, `gerar_manifest.py` e o campo `formato` no `index.json`.
2. `site.yml` atualizado (o usuário aplica) e passo de orçamento.
3. `docs/motor.md`.
4. Conferir no Pages publicado o manifesto, os hashes e o cabeçalho `Access-Control-Allow-Origin`.

### Frontend

**PR F1, infraestrutura sem UI** (depende do B3 publicado):

1. `sync-motor.mjs`, `vendor/`, `check:motor` e a suíte de conformidade.
2. `acervo.server.ts`, `limites.server.ts` e `contrato.ts`.
3. As rotas `caso.ts` e `saude.ts`, com seus testes.

**PR F2, janela:**

1. Adaptador, hook e componentes da janela.
2. Botão novo em `relatorio.$id.tsx`, ao lado do painel antigo (os dois coexistem só nesta etapa).
3. Conferência manual contra o site.

**PR F3, remoção do legado:**

1. Remover:
   - `src/lib/legislation/*`;
   - `legislation.functions.ts`, `use-legislation-consultation.ts` e `LegislationPanel.tsx`;
   - `n8n/analise-legislacao/` e `docs/consulta-legislacao.md`;
   - `tests/legislation*.test.ts` e `scripts/test-legislation*.mjs`.
2. Ajustar os scripts do `package.json`: tirar `test:legislation*`, `test:n8n` e `build:n8n`; incluir `sync:motor`, `check:motor` e `test:consulta`.
3. Retirar as variáveis `N8N_LEGISLATION_*`, `LEGISLATION_AI_MODEL`, `LEGISLATION_GITHUB_TOKEN` e `LEGISLATION_COMMIT`. A `LOVABLE_API_KEY` sai também, se nada mais a usar.
4. Criar `docs/api-consulta-caso.md`.

## Riscos

- **R1. CPU e memória no Cloudflare.** O índice pré-computado não basta sozinho: o `JSON.parse` de cerca de 10 MB e a hidratação ainda custam CPU, e o teto real é a memória da isolate (128 MB).
  - No plano gratuito (10 ms de CPU), o desenho não funciona. No pago (padrão de 30 s), provavelmente funciona.
  - Não se sabe qual plano o Lovable usa, por isso a Etapa 0 é condição para seguir.
  - **Plano B, com o mesmo contrato:** rodar o motor no navegador. O Pages já libera CORS (`*`), então o navegador importa `motor/index.js` direto do Pages e a "API" vira uma função local com a mesma saída `busca-caso/1`.
  - Para permitir essa troca, `cliente.ts` fica atrás de uma interface de transporte.
- **R2. Acervo 10 vezes maior.** A varredura linear e os `Map` por bloco não escalam (estimativa de ~400 MB de memória). O caminho é o `formato: 2`: índice invertido, com o texto em shards baixados só para os candidatos. O versionamento de `formato` permite essa troca sem quebrar o contrato.
- **R3. Commit divergente durante um deploy.** Só o `index.json` traz o commit; `cnae.json`, `sinonimos.json` e `ambitos.json` não trazem. O sha256 por arquivo no manifesto cobre todos.
- **R4. Rate limit fraco.** O limite em memória vale por isolate. O recomendado é uma regra de rate limiting no painel da Cloudflare. Sem acesso a esse painel, o risco é aceito para o volume atual.
- **R5. Endpoint público.** "Quem abre o rascunho" descreve a UX; o endpoint em si é público.
- **R6. `casos-auditoria.json` não serve de golden.** Os `esperados` foram escritos para a busca lexical em Python e para consultas livres. O teste de paridade de verdade é o golden do mini-acervo, mais o `caso-formulario.json`.
- **R7. Golden sobre o acervo real** quebraria a cada norma nova. Por isso o golden usa o mini-acervo.
- **R8. Workflows** precisam ser criados pelo usuário (limite do token da sessão na nuvem).
- **R9. Sincronização manual do vendor.** O Lovable não tem CI. O `check:motor` fica manual, e o `/saude` mostra `motor.compativel` para sinalizar defasagem em produção.

## Perguntas abertas (com o padrão adotado)

1. **Plano da Cloudflare no Lovable.** Padrão: assumir plano pago e confirmar na Etapa 0.
2. **Atividade vazia com CNAE presente.** Padrão: não derivar a atividade da descrição do CNAE, como o site.
3. **Modalidades.** Padrão: incluir `rlas` como opção nova; mapear ampliação e regularização para os códigos genéricos.
4. **Mais de um valor detectado** (por exemplo, poço e rede). Padrão: um valor só, por precedência, com todos os termos listados na proveniência. Para o `busca-caso/2`, aceitar uma lista e criar um eixo por valor.
5. **Até 6 termos num único eixo diluem o score** (`(ok/n)²`, index.html:270). Padrão: manter, para ficar igual ao site. Evolução possível: um eixo por termo.
6. **Edições manuais ao fechar e reabrir a janela.** Padrão: ficam em memória enquanto o rascunho está aberto e são descartadas se o mapeamento do rascunho mudar.
7. **Limites da resposta.** O padrão é 10 normas por eixo, 6 trechos por norma e 1.200 caracteres por trecho, menos do que o site mostra. Padrão: aceitar, exibindo `totalNormas` e `totalTrechos` para não esconder o corte.
8. **CNAE "compreende / não compreende"** fica fora da resposta. Padrão: link para o site.
