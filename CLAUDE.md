# Instruções para o agente

Antes de converter ou atualizar qualquer norma, leia o README.md: ele define o padrão (nomes, IDs LexML, links, tags e o tratamento de alterações e revogações).

Regras principais:
- Nunca apague o arquivo de uma norma alterada ou revogada. Atualize-o como texto compilado.
- Transcreva o texto exatamente como publicado e registre os erros do original em "Notas de transcrição".
- Anexos: siga a seção "Anexos" do README (tipo 1: modelo, só o nome; tipo 2: diretriz de estudo, arquivo próprio em normas/anexos/ com síntese separada e fontes; tipo 3: normativo, lista com IDs anexoN_linM ou anexoN_tabT_linM). Consulte glossario.md antes de pesquisar termos na web.
- Rode `python scripts/validar.py` e só faça commit com 0 erros.
- Mostre as mudanças ao usuário antes do commit e sinalize revogação tácita, remissões erradas e vigência diferida.
- Mensagem de commit: `norma: <arquivo> (nova | altera <arquivo> | revoga <arquivo>)`.

## Comportamento Adaptativo

Habilidades e memória formam um único sistema cognitivo. Habilidades = memória procedural ("como fazer as coisas", memória muscular). Memória = memória declarativa ("o que eu sei", memória consciente). Elas alimentam uma à outra.

### Regras Sempre Ativas

Aplicam-se a todas as sessões, sem precisar invocar uma habilidade:

* **Autoaperfeiçoamento de habilidades**: Quando uma habilidade encontrar atrito (falha em etapa, necessidade de contorno), corrija o problema E atualize o arquivo da habilidade — adicione uma seção `## Gotchas` (armadilhas/cuidados) ou atualize as etapas. Salve também na memória se a lição for útil para outras habilidades.
* **Fluxo Memória → Habilidade**: Antes de executar uma habilidade, verifique a memória e as armadilhas em busca de lições relevantes. Aplique-as de forma proativa.
* **Detecção de lacunas de habilidades**: Quando um fluxo de trabalho com várias etapas se repetir entre sessões e nenhuma habilidade existir, crie uma.

### Fluxos de Trabalho Estruturados

Para revisões mais profundas e gerenciamento de perfil, utilize as habilidades dedicadas:

* `/skill-review` — revisão periódica de todas as habilidades quanto à obsolescência, armadilhas ausentes e consolidação.
* `/build-user-profile` — cria ou atualiza o perfil do usuário a partir do contexto do workspace.
