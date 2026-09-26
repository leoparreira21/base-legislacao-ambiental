# Base de Legislação Ambiental (Markdown)

Normas de licenciamento ambiental convertidas em Markdown, uma norma por arquivo, com identificação de cada dispositivo, links entre normas e tags temáticas. Pensada para consulta por IA (RAG) e para leitura no Obsidian.

## Estrutura

```
normas/            um arquivo .md por norma
scripts/validar.py validação da base (rodar antes de cada commit)
tags.md            lista das tags em uso (gerada pelo script)
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

## Alterações e revogações (texto compilado)

Quando uma norma nova altera, acrescenta ou revoga dispositivos de outra, **o arquivo da norma afetada é atualizado, nunca apagado**. O texto antigo ainda rege processos protocolados antes da mudança (ver, por exemplo, o art. 173 do Decreto 9.541/2025), e outras normas linkam para ele.

| Caso | Como fica no arquivo da norma afetada |
|---|---|
| Nova redação | O texto novo fica no lugar, seguido de `*(Redação dada pelo [[norma-nova#artN\|Decreto nº X/AAAA]])*`. A redação original fica logo abaixo, tachada: `> Redação original: ~~...~~`. O dispositivo recebe `#redacao-alterada`. |
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
