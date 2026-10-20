# Pré-classificação funcional dos dispositivos

As cinco funções são metadados editoriais, separados da transcrição normativa. Não certificam vigência ou aplicabilidade ao caso. Um dispositivo pode ter várias funções. A aplicabilidade (`aplicavel`, `condicionada`, etc.) continua sendo um campo independente no chat.

| Categoria | Critério inicial |
|---|---|
| Específicas para enquadramento | Atividade, CNAE, porte, potencial poluidor e sujeição/dispensa |
| Específicas para licenciamento | Modalidade, requerimento, renovação, documentos, estudos e rito |
| Obrigações e proibições | Conduta obrigatória, vedada ou permitida sob condição |
| Limites de parâmetros | Valores ambientais quantitativos e unidades/padrões técnicos |
| Normas gerais | Princípios, definições, disposições gerais e classificação residual quando não há sinal reconhecido |

## Alcance e limites

O classificador `scripts/classificar_dispositivos.py` usa regras determinísticas e sinais no próprio dispositivo, sem inferência paga e sem pesquisa externa. Tags e rótulos são retirados antes da classificação. Contexto do pai pode ajudar a reconhecer unidade de linha numérica de tabela. Prazos e limites de porte não são tratados automaticamente como limites ambientais. A simples menção a padrões ou à composição comercial de um produto não fixa limite ambiental.

Primeira execução: 38.272 dispositivos elegíveis receberam sugestões. Ocorrências por categoria (podem se sobrepor): enquadramento 2.431; licenciamento 2.757; obrigações/proibições 3.928; limites 988; gerais/residual 29.617. Estes números medem cobertura das regras, **não precisão semântica**. A categoria residual é ampla e exige revisão prioritária. Incisos curtos que dependem do comando do pai podem precisar de correção manual; não se herda indiscriminadamente a função do artigo inteiro.

Revogados cadastrados, redações antigas excluídas pelo extrator e comentários interpretativos não entram nas sugestões elegíveis. Cabeçalhos estruturais com ID podem aparecer como gerais/residuais. Não houve revisão jurídica individual de todos os registros.

## Conferir e corrigir

1. Abra **Revisar a classificação funcional dos dispositivos** na busca, ou `classificacao.html`.
2. Filtre por norma, categoria, estado ou texto/ID. Confira a íntegra e os motivos da sugestão.
3. Marque uma ou mais categorias e confirme a revisão de cada dispositivo.
4. Exporte `classificacao-revisada.json`. As alterações da sessão não são gravadas remotamente pelo navegador. É possível importar o arquivo para continuar.
5. Substitua `consultas/classificacao-revisada.json` pelo arquivo exportado e publique pelo fluxo habitual do repositório.

O arquivo contém objetos por `norma#id`, com `categorias` e `texto_sha256`. Revisões válidas prevalecem sobre a sugestão. Alteração da redação invalida a revisão antiga e volta a marcar a sugestão para conferência. IDs/categorias inexistentes fazem o build falhar; importação pela interface rejeita integralmente um arquivo inválido ou de outra redação antes de alterar a sessão. O export inclui revisões já publicadas e as confirmadas na sessão.

## Busca, grafo e chat

O grafo e `classificacao.json` recebem o campo `funcao`. As fatias do Worker levam apenas categorias e estado, para controlar memória. O índice da busca mantém os oito campos anteriores e acrescenta um campo opcional com a união das funções dos dispositivos do trecho. O filtro da busca opera sobre esse trecho; a revisão opera por ID exato. A versão do motor passa a 1.3.0; consumidores antigos podem ignorar o novo campo adicional.

O servidor preenche a função de cada item do chat a partir da fonte recuperada; não aceita uma categoria inventada pela IA como metadado canônico. O prompt diferencia função editorial de evidência normativa.

## Verificação

Build local, validador da base (0 erros, 146 avisos preexistentes), validador de índices/fatias (0 erros), testes Python de classificação e grafo, 30 testes Node de motor/classificação/contrato, integração do chat com IA simulada e 25 testes de memória (motor + 24 casos). Sem chamada paga de IA para classificar. Não foi concluída uma verificação visual em navegador neste ambiente; não se declara auditoria visual ou semântica integral.

Comandos: `python scripts/gerar_site.py _site`; `python scripts/validar_indices.py _site`; `python -m unittest discover -s testes -v`; `node --test testes/motor.test.mjs testes/classificacao.test.mjs testes/worker-contract.test.mjs`; `SITE_DIR=_site node --test testes/worker-integracao.test.mjs` (definir a variável de acordo com o shell).
