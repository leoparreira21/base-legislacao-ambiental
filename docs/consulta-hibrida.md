# Consulta híbrida — infraestrutura do repositório

## Situação
Esta implantação prepara índices, testes e contratos, sem criar servidor de IA.
O site estático e seu motor lexical continuam compatíveis.
GitHub Pages não executa modelos nem deve armazenar chaves secretas.

## Artefatos publicados
- manifesto.json: SHA e hashes SHA-256 dos arquivos publicados.
- index.json e motor.js: recuperação lexical atual.
- dispositivos.json (dispositivos/1): IDs, texto original, linhas, hierarquia,
  tags, natureza, situação cadastrada e remissões.
- grafo.json (grafo/1): arestas explícitas e destinos pendentes.
- cnae.json, ambitos.json e sinonimos.json: filtros atuais.

A chave é composta por nome da norma e âncora: resolucao-conama-430-2011#art1_par1u.
Não confundir a ocorrência de um wikilink com aplicabilidade ou revogação.

## Regras essenciais de interpretação
- natureza texto-normativo: texto transcrito do acervo.
- natureza interpretativo: comentário ou anotação editorial, nunca exigência.
- situacao revogado/revogada: excluído de fundamentação positiva.
- situacao vigencia_nao_certificada: NÃO significa vigência jurídica confirmada.
- elegivel: filtro mecânico, não parecer jurídico.
- tags herdadas não propagam marcadores de revogação ou alteração.
- relacoes nao resolvidas devem permanecer visíveis como lacunas.

## Pipeline futuro — servidor externo de IA ainda não escolhido
1. Receber dados essenciais do empreendimento, distinguindo desconhecidos.
2. Fixar manifesto.commit e verificar hashes dos índices.
3. Usar a busca lexical existente com eixos, CNAEs e âmbitos para obter candidatos.
4. Resolver os IDs no índice de dispositivos; expandir pais, remissões e
   alteradoras com profundidade limitada, preservando origem de cada evidência.
5. Enviar SOMENTE o conjunto recuperado para a IA junto ao prompt do agente.
6. Exigir JSON no contrato consultas/contrato-resposta.schema.json.
7. Checar a resposta com scripts/validar_resposta.py, checagem de schema e
   revisão de mérito antes de assumir exigências.
8. Exibir links para arquivos exatos por commit e linhas:
   https://github.com/leoparreira21/base-legislacao-ambiental/blob/COMMIT/ARQUIVO#L10-L15

A integridade das citações não assegura interpretação jurídica correta.
O agente deve responder insuficiência de dados quando necessário.

## Comandos de verificação
    python scripts/validar.py
    python -m unittest discover -s testes -v
    python scripts/gerar_site.py _site
    python scripts/validar_indices.py _site
    node --test testes/motor.test.mjs
    python scripts/validar_resposta.py resposta.json _site/dispositivos.json

O último comando depende de uma resposta JSON, ainda não produzida.

## Fora do escopo
Não há provedor de IA, endpoint HTTP, chaves, integração IAT Report Builder
ou aba de IA funcional. Estas etapas dependem da escolha do servidor externo.
GitHub Actions publica o site apenas na main e testa PRs separadamente.
