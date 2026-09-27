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

As sessões na nuvem começam do zero: a memória do agente e as edições em habilidades do claude.ai se perdem quando a sessão termina. O que precisa sobreviver entre sessões fica no repositório, em `licoes.md`.

- **Antes de trabalhar**: leia `licoes.md` e aplique as lições relevantes à tarefa.
- **Ao encontrar atrito** (etapa que falhou, contorno necessário, regra do README ambígua): corrija o problema e registre a lição em `licoes.md`, no mesmo commit. Se a lição mudar o padrão da base, proponha a mudança no README em vez de só anotá-la.
- **Habilidades do claude.ai** (`base-legislacao` e outras): não são versionadas aqui e não podem ser alteradas de forma permanente pela sessão. Quando uma delas precisar de ajuste, registre a lição em `licoes.md` e diga ao usuário qual trecho da habilidade mudar, com o texto sugerido.
- **Fluxo repetido sem habilidade**: se `licoes.md` mostrar o mesmo fluxo de várias etapas em sessões diferentes, sugira ao usuário criar uma habilidade para ele.
- **Revisão**: quando `licoes.md` passar de umas 30 lições, ou a pedido do usuário, consolide as lições duplicadas ou obsoletas e leve as permanentes para o README.
