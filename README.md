# Base de Legislação Ambiental (Markdown)

Normas de licenciamento ambiental convertidas em Markdown, uma norma por arquivo, com identificação de cada dispositivo, links entre normas e tags temáticas. Pensada para consulta por IA (RAG) e para leitura no Obsidian.

## Estrutura

```
normas/            um arquivo .md por norma
normas/anexos/     anexos de diretrizes de estudos e termos de referência (tipo 2), um arquivo por anexo
normas/comentarios/ comentários oficiais a uma norma (ex.: versão comentada da Anvisa), um arquivo por documento
scripts/validar.py validação da base (rodar antes de cada commit)
tags.md            lista das tags em uso (gerada pelo script)
glossario.md       termos técnicos já pesquisados, com fonte (reaproveitado pelos agentes)
licoes.md          armadilhas e contornos registrados pelos agentes (ver CLAUDE.md)
```

## Padrão das normas

### Nome do arquivo
`tipo-orgao/esfera-numero-ano.md`, tudo em minúsculas, sem acento e sem pontos no número.
Exemplos: `lei-estadual-22252-2024`, `decreto-estadual-9541-2025`, `resolucao-cema-107-2020`, `lei-federal-12651-2012`, `lei-complementar-federal-140-2011`, `resolucao-conjunta-sedest-iat-6-2023`.

### Frontmatter
```yaml
norma: Decreto Estadual nº 9.541/2025
arquivo: decreto-estadual-9541-2025      # igual ao nome do arquivo
tipo: decreto
esfera: estadual
uf: PR
numero: 9541
ano: 2025
data_assinatura: 2025-04-10
ementa: "..."
situacao: vigente                        # vigente | revogada
regulamenta: ["[[lei-estadual-22252-2024]]"]
regulamentado_por: []                    # só em leis
altera: []
alterado_por: ["[[decreto-estadual-12799-2026]]"]
revoga: [...]
revogado_por: []
cita: [...]
tags: [...]                              # todas as tags usadas no corpo
fonte: ...
```
As relações são **recíprocas**: se A `altera` B, B tem A em `alterado_por`. O mesmo vale para `revoga`/`revogado_por` e `regulamenta`/`regulamentado_por`.

### Hierarquia e IDs (padrão LexML)
| Dispositivo | ID | Exemplo de rótulo |
|---|---|---|
| Artigo | `art5` | `###### Art. 5º {#art5}` |
| Caput | `art5_cpt` | `**Art. 5º, caput** {#art5_cpt}` |
| Parágrafo | `art5_par2` | `**Art. 5º, § 2º** {#art5_par2}` |
| Parágrafo único | `art5_par1u` | `**Art. 5º, parágrafo único** {#art5_par1u}` |
| Inciso do caput | `art5_cpt_inc3` | `- **Art. 5º, caput, inciso III** {#art5_cpt_inc3}` |
| Inciso de parágrafo | `art5_par2_inc3` | `- **Art. 5º, § 2º, inciso III** {#art5_par2_inc3}` |
| Alínea | `art5_cpt_inc3_alia` | `  - **Art. 5º, caput, inciso III, alínea "a"** {#art5_cpt_inc3_alia}` |
| Item | `art5_cpt_inc3_alia_ite1` | |
| Artigo com letra (Art. 5º-A) | `art5-a` | |
| Tabela no corpo de um artigo | `art14_tab1` | `**Art. 14, Tabela I**` |
| Linha de tabela no corpo de um artigo | `art14_tab1_lin3` | `- **Art. 14, Tabela I, linha 3**` |

Títulos, capítulos e seções usam `##`, `###`, `####` e `#####`; artigos usam `######`. Abaixo do cabeçalho de cada artigo vai uma linha `Tags:` com as tags do artigo inteiro.

### Links
- Para outra norma: `[[lei-federal-12651-2012#art3|incisos VIII e IX do art. 3º da Lei 12.651/2012]]`
- Dentro da mesma norma: `[[#art13_cpt_inc4|inciso IV]]`
- Uma norma que ainda não está na base recebe o link mesmo assim. Ele fica pendente e passa a funcionar quando o arquivo for adicionado com esse nome.

### Tags
- Na linha `Tags:` do artigo e, quando o tema for específico, logo após o rótulo do dispositivo: `**Art. 30, caput, inciso VIII** {#art30_cpt_inc8} #manancial ...`
- Formato: minúsculas, sem acento, singular, hífen entre palavras (`#supressao-vegetacao`).
- Reaproveite as tags de `tags.md` antes de criar uma nova.
- Tags de controle: `#revogado`, `#redacao-alterada`, `#incluido`.

### Fidelidade ao texto
O texto é transcrito **exatamente como publicado**, com os erros do original. Os erros ficam registrados na seção final `## Notas de transcrição`, e os links seguem a letra da norma, salvo exceção registrada nessa seção.

## Anexos

Todo anexo tem uma seção no arquivo da norma: `### ANEXO V {#anexo5}`. O tratamento depende do conteúdo, e um mesmo anexo pode combinar tipos (cada parte segue a sua regra).

### Tipo 1: modelos (declarações, certidões, formulários, ART)
O conteúdo não é transcrito. A seção traz só uma linha: `Modelo de declaração de <nome da declaração>` (ou `Modelo de certidão de ...`, `Modelo de ...`), usando o nome dado pelo próprio texto da norma.

### Tipo 2: diretrizes de estudos técnicos e termos de referência
Vão para um arquivo próprio em `normas/anexos/<arquivo-da-norma>-anexoN.md`, invocado só quando a atividade corresponde. No arquivo da norma, a seção do anexo tem apenas o título e o link para esse arquivo.

Frontmatter do arquivo do anexo:
```yaml
anexo: ANEXO VIII
norma_mae: "[[instrucao-normativa-iat-65-2025]]"
arquivo: instrucao-normativa-iat-65-2025-anexo8
tipo_anexo: diretriz-estudo            # diretriz-estudo | termo-referencia
estudo: PBCA                           # sigla do estudo
atividades: [industria]                # atividades às quais o anexo se aplica
modalidades: [las, lasa, lasr]         # licenças em que o estudo é exigido
tags: [...]
```
Corpo, em duas partes separadas:
1. `## Texto do anexo`: transcrição fiel, com IDs `anexo8_lin1`, `anexo8_tab2_lin3`.
2. `## Síntese do conversor (não é texto normativo)`: o que o estudo deve conter, organizado por tópico, com os termos técnicos explicados e as **fontes citadas**. Os termos pesquisados entram também no `glossario.md`.

Procedimento (subagentes): (a) localizar a atividade e as modalidades a que o anexo se aplica; (b) interpretação do texto técnico; (c) pesquisa na web dos termos e expressões sem contexto, consultando antes o `glossario.md`; (d) organização em Markdown no padrão da base.

### Tipo 3: conteúdo normativo (definições institucionais, regulamentações, limites quantitativos, condições, enquadramento)
É tratado como norma, igual ao corpo principal, e fica no arquivo da norma como lista, uma entrada por disposição ou linha de tabela:
- disposição do texto do anexo: `{#anexo5_lin2}` (2ª disposição do ANEXO V);
- linha de tabela: `{#anexo5_tab3_lin2}` (2ª linha da Tabela 3 do ANEXO V).

Cada entrada é autossuficiente: células mescladas são desfeitas repetindo o valor em cada linha, linhas partidas entre páginas são unidas e cabeçalhos repetidos por página são removidos (registrar isso nas Notas de transcrição). Formato de uma linha de tabela:
```markdown
- **Anexo II, Tabela 1, linha 6** {#anexo2_tab1_lin6} #industria-madeira Tipologia: Ind. da madeira | Atividade: Fabricação de móveis com predominância de madeira | Limite: Área até 2.000 m²; Não utilize matéria prima de origem nativa.
```
Tabelas são lidas das imagens das páginas, não do texto extraído, e o número de linhas é conferido contra o PDF.

Tabelas que ficam no corpo de um artigo (e não num anexo), como os padrões de qualidade das resoluções CONAMA, seguem as mesmas regras, com ID `artN_tabT_linM`, em que T é o número da tabela no original (Tabela I = 1). Tabela sem título nem número no original (em artigo ou anexo) é numerada pelo conversor na ordem em que aparece na norma, com um título descritivo marcado "(sem título no original)", e o tratamento fica registrado nas Notas de transcrição. Formato:
```markdown
- **Art. 14, Tabela I, linha 4** {#art14_tab1_lin4} PARÂMETROS INORGÂNICOS: Alumínio dissolvido | VALOR MÁXIMO: 0,1 mg/L Al
```

## Comentários oficiais

Documentos interpretativos publicados pelo órgão (por exemplo, a "RDC nº 222/2018 Comentada" da Anvisa) não são texto normativo e ficam separados da norma, em `normas/comentarios/<arquivo-da-norma>-coment.md`.

Frontmatter:
```yaml
documento: RDC nº 222/2018 Comentada
norma_mae: "[[rdc-anvisa-222-2018]]"
arquivo: rdc-anvisa-222-2018-coment
tipo_documento: comentario
autor: "..."
data: 2018-06-11
natureza: "Orientação interpretativa ..., sem força normativa."
cita: [...]
tags: [...]
fonte: "..."
```

Cada comentário leva o ID do dispositivo comentado com o sufixo `_coment` e começa com o link direto para ele:
```markdown
**Comentário: Art. 5º, § 1º** {#art5_par1_coment} → [[rdc-anvisa-222-2018#art5_par1|Art. 5º, § 1º]]

Texto do comentário...
```
Na norma, o dispositivo comentado termina com o link de volta: `[[rdc-anvisa-222-2018-coment#art5_par1_coment|(comentário)]]`, e o frontmatter da norma aponta o arquivo em `comentarios:`. Comentários gerais de capítulo ou seção usam o ID do título na norma (`cap3_sec1` → `cap3_sec1_coment`); por isso, nas normas com comentários, capítulos e seções recebem ID (`## CAPÍTULO III – ... {#cap3}`, `### Seção I – ... {#cap3_sec1}`). O arquivo de comentários não repete o texto dos dispositivos: vale o texto oficial, e as diferenças entre a versão comentada e a oficial ficam nas notas de transcrição da norma. O `validar.py` confere se cada `X_coment` tem o dispositivo `X` na norma-mãe.

## Alterações e revogações (texto compilado)

Quando uma norma nova altera, acrescenta ou revoga dispositivos de outra, **o arquivo da norma afetada é atualizado, nunca apagado**. O texto antigo ainda rege processos protocolados antes da mudança (ver, por exemplo, o art. 173 do Decreto 9.541/2025), e outras normas linkam para ele.

| Caso | Como fica no arquivo da norma afetada |
|---|---|
| Nova redação | O texto novo fica no lugar, seguido de `*(Redação dada pelo [[norma-nova#artN\|Decreto nº X/AAAA]])*`. A redação original fica logo abaixo, tachada: `> Redação original: ~~...~~`. Se houve mais de uma alteração, as redações intermediárias vêm em seguida, na ordem: `> Redação anterior: ~~...~~ *(Redação dada pela [[...]])*`. O dispositivo recebe `#redacao-alterada`. |
| Dispositivo acrescentado | É inserido na posição correta, com ID novo, `#incluido` e `*(Incluído pelo [[...]])*`. |
| Revogação de dispositivo | O texto fica tachado `~~...~~`, com `#revogado` e `*(Revogado pelo [[...]])*`. O ID não muda. |
| Revogação total | O arquivo é mantido, com `situacao: revogada` e `revogado_por` preenchido. |

Além disso:
- A linha `Alterações:` abaixo das `Tags:` do artigo resume o que mudou.
- A tabela `## Histórico de alterações`, antes das notas de transcrição, registra cada mudança.
- O campo `texto: compilado (atualizado até ...)` fica no frontmatter.
- Na norma alteradora, cada nova redação aparece em citação (`>`) com ID próprio (`art1_cpt_alt1`) e link para o dispositivo alterado.

Para buscar só o texto em vigor, exclua `#revogado` e as linhas tachadas.

## Validação
```
python scripts/validar.py                          # erros bloqueiam o commit
python scripts/validar.py --tags                   # atualiza tags.md
python scripts/validar.py --afetados NOME-DA-NORMA # outras normas que apontam para dispositivos revogados ou alterados
```
