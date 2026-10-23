# Integração com ctresb-leis

A consulta combina a base curada com um snapshot complementar de
`leoparreira21/ctresb-leis`. Nenhum conteúdo de `normas/` é substituído.
O recorte inicial contém resoluções CONAMA e instruções normativas IBAMA.
A cobertura não é todo o acervo brasileiro: o snapshot de origem traz apenas
sete resoluções CONAMA. Ausência de resultado nunca prova ausência de obrigação.

## Fluxo

1. `scripts/sincronizar_ctresb.py` lê arquivos de um commit Git explícito.
2. `consultas/ctresb-index.json` registra commit, caminho, SHA-256 do texto,
   fonte oficial, versão textual, artigos literais e linhas de origem.
3. O build copia esse índice e publica seu hash no manifesto. Remove novamente
   duplicatas que tenham sido incorporadas à base curada desde a sincronização.
4. `site/complementar.js` recupera candidatos no navegador e no Worker.
5. A API confere o hash antes de usar o complemento. Falha isolada deixa a base
   principal disponível e gera aviso. A IA só cita trechos efetivamente recuperados.

O navegador mostra uma seção separada nas buscas livres e nos casos. A API
`/candidatos` adiciona `complementares` e `avisos`, preservando `eixos` existentes.
`/analisar` e `/chat` acrescentam até quatro artigos principais e o âmbito inicial
(arts. 1 e 2), sujeitos ao orçamento total existente. Não há nova inferência,
credencial, serviço pago ou consulta ao GitHub por pergunta.

## Garantias e limites

- Termos cumulativos, com cobertura mínima de 65% e pelo menos dois termos quando
  disponíveis; referência explícita exige órgão/número e ano, se informado.
- Artigos inteiros preservam parágrafos e incisos. Texto longo enviado à IA é
  marcado parcial. IDs externos usam `ctresb:` e não simulam IDs LexML revisados.
- Não há equivalência automática entre similaridade textual e aplicabilidade.
  Qualquer conclusão apoiada em texto complementar é, no máximo, condicionada.
- Situação desconhecida não vira vigente. Excluem-se normas marcadas revogadas,
  artigos tachados, numeração repetida e identidades duplicadas; a lista de
  exclusões fica no índice. Não se decide revogação tácita nem vigência diferida.
- Anexos externos não são indexados nesta etapa; ficam na íntegra vinculada.
  Classificação funcional, CNAE e relações do grafo não são inventados para
  textos externos. O filtro funcional oculta o complemento e explica a razão.
- A consulta por caso usa atividade para candidatos complementares na tela; a IA
  também busca pela pergunta, resíduos, outros fatos e localização, separadamente.
- As normas importadas não passaram por conferência jurídica nem revisão de OCR.
  Verifique publicação oficial, alterações, ressalvas e âmbito antes de aplicar.

## Atualizar o snapshot

Em uma cópia local do repositório complementar:

```sh
git -C ../ctresb-leis fetch origin main
python scripts/sincronizar_ctresb.py ../ctresb-leis --ref origin/main
python scripts/validar.py
python -m unittest discover -s testes -v
python scripts/gerar_site.py _site
python scripts/validar_indices.py _site
node --test testes/complementar.test.mjs testes/worker-contract.test.mjs testes/motor.test.mjs
SITE_DIR=_site node --test testes/worker-integracao.test.mjs testes/worker-memoria.test.mjs
```

O build não baixa conteúdo remoto e não atualiza o snapshot silenciosamente.
Revise o diff e as exclusões em um PR. A rotina limita o índice a 8 MB e preserva
seu arquivo anterior quando falha. Para ampliar o recorte, edite `PREFIXES` e
revise identidade, jurisdição e pertinência antes de incluir outros órgãos.
Para centenas de milhares de documentos, será necessário índice fragmentado ou
busca no servidor; não carregar o acervo integral no navegador/Worker.

## Publicação e reversão

Após o merge, `site.yml` publica o índice e o site; `implantar-worker.yml` publica
em seguida o Worker. Não é necessário alterar secrets ou wrangler. O Worker novo
aceita manifesto antigo sem complemento. Reverter o PR restaura a busca anterior.

## Verificação desta entrega

Testes de importação, seleção, referências e citações; regressões Python e Node;
integração com índices reais e IA simulada. A resposta do modelo real e o deploy
em produção devem ser conferidos após o merge. Nenhuma norma foi promovida a
texto curado ou marcada vigente pela importação.
