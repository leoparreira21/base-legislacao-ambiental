# Lições aprendidas

Armadilhas e contornos encontrados pelos agentes ao converter e atualizar normas. Leia antes de começar; acrescente ao encontrar atrito (ver "Comportamento Adaptativo" no CLAUDE.md).

Formato: uma lição por item, com data, contexto e o que fazer.

```
- AAAA-MM-DD, <norma ou etapa>: <o que deu errado>. Fazer: <como evitar ou contornar>.
```

## Conversão de PDF

- 2026-09-27, entrada dos PDFs: o pedido apontava uma pasta local do Windows (`C:\Users\...`), que a sessão na nuvem não alcança (container isolado; também não havia a pasta no Google Drive nem PDFs no repositório). Fazer: pedir ao usuário que anexe os PDFs na conversa ou os envie ao repositório (por exemplo, em `entrada/` num ramo) antes de começar; não tentar adivinhar o conteúdo.
- 2026-09-27, ambiente da nuvem: `pdftotext`/`pdfinfo` não vêm instalados. Fazer: `apt-get install -y poppler-utils` e `pip install pymupdf` (PyMuPDF também lê tabelas com `page.find_tables()`, que respeita as linhas de grade e acerta a estrutura das linhas).
- 2026-09-27, textos compilados (Planalto, portal do CONAMA): o `pdftotext` perde o tachado das redações anteriores, e o texto antigo sai misturado com o novo. Fazer: detectar o tachado com PyMuPDF (segmentos horizontais finos que cruzam o meio dos caracteres) e marcar `~~`; depois, casar cada versão tachada com a versão em vigor de mesmo ID. As anotações "(Redação dada ...)" às vezes caem numa linha separada: reunir ao dispositivo.
- 2026-09-27, texto atualizado da Câmara dos Deputados (Lei 12.305/2010): mostra só a redação em vigor, sem a original. Fazer: buscar a redação original (DOU/Planalto), registrar nas Notas de transcrição que ela não vem do PDF e pedir conferência ao usuário.
- 2026-09-27, PDFs do CONAMA: o "o" sobrescrito dos ordinais ("Art. 2o") sai numa linha separada no `pdftotext`, e letras gregas em fonte Symbol viram caracteres de uso privado (U+F061 = α, U+F062 = β, U+F067 = γ), que o PDF mostra como quadrados. Fazer: juntar o sobrescrito à linha pelo bbox (PyMuPDF) e decodificar os caracteres de uso privado, registrando nas notas.
- 2026-09-27, normas longas: gerar tudo por script (texto extraído → parágrafos → dispositivos com ID), deixando tags, links e tabelas num arquivo de configuração por norma, e conferir por `difflib` contra o PDF. Para textos compilados, em que a ordem das versões muda, conferir pela contagem de palavras (`collections.Counter`) em vez da sequência.
- 2026-09-27, IN IAT 11/2026 ("Microsoft Print to PDF"): cada linha vem gravada em pedaços sobrepostos e recortados; o `pdftotext` repete trechos e corta palavras ("Lei ederal", "Negócioss"). Fazer: reconstruir o texto caractere a caractere com PyMuPDF (`rawdict`), deduplicando por posição (x, linha de base) e descartando o caractere igual a menos de ~2,5 pt do anterior; conferir por `difflib` e nas imagens.
- 2026-09-27, obter o PDF oficial: o site do IAT (www.iat.pr.gov.br) responde pelo shell da nuvem. A página "Instruções Normativas / Orientações Técnicas" traz os links `.../arquivos_restritos/files/documento/AAAA-MM/<nome>.pdf`. Fazer: quando o usuário mandar só a extração de texto, baixar o PDF oficial dali para ler tabelas e conferir imagens.

- 2026-09-27, RDC Anvisa 222/2018 Comentada (texto justificado): o `get_text()` do PyMuPDF quebra as linhas justificadas em pedaços ("encaminhados \npara \nreciclagem") e mistura numeral e texto de incisos que ficam em colunas. Fazer: ler com `get_text('dict')`, agrupar os pedaços pela linha de base (tolerância de uns 4 pt) e marcar fim de parágrafo quando a linha termina antes da margem direita.
- 2026-09-27, versão comentada de uma norma: separar comentário de dispositivo por alinhamento com o texto oficial já estruturado (texto normalizado só com letras e números; início pelos primeiros 40 caracteres do dispositivo, fim pelos últimos 30), não por regex de "Art."/"§". Onde a versão comentada muda o final do dispositivo, cortar palavras do fim até achar o término. Conferir depois as diferenças de texto entre as duas versões e registrá-las nas notas.

## Anexos

- 2026-09-27, CONAMA 357/2005 e 430/2011: as tabelas de padrões ficam no corpo dos artigos, não em anexos, e o README só previa IDs `anexoN_tabT_linM`. Fazer: usar `artN_tabT_linM` (T = número da tabela no original), com as mesmas regras do tipo 3. Proposta incluída no README.
- 2026-09-27, IN IAT 11/2026, tabela de 118 páginas: `find_tables()` fragmentou as células (grade irregular). Fazer: usar como faixas de linha os segmentos verticais da borda esquerda da tabela (`get_drawings()`), atribuir os caracteres às colunas pelo x das linhas verticais, unir as faixas sem código na 1ª coluna à linha anterior (continuação entre páginas) e conferir a contagem de linhas contra os códigos distintos do `pdftotext`.
- 2026-09-27, "ANEXO ÚNICO": o README só prevê `anexoN`. Usado `anexo1` e `anexo1_tab1_linM` (tabela sem título tratada como Tabela 1). Inciso sem número no original (IN IAT 11/2026, art. 3º, "forma de atuação" entre VIII e IX): usado `art3_cpt_inc8-a`, registrado nas Notas. Proposta: incluir as duas convenções no README.

## Alterações e revogações

- 2026-09-27, Lei 9.433/1997: um mesmo dispositivo teve várias redações sucessivas (MP 870/2019, Lei 13.844/2019, MP 1.154/2023, Lei 14.600/2023), e o README só previa "Redação original". Fazer: após a redação original, listar as intermediárias como `> Redação anterior: ~~...~~ *(Redação dada pela [[...]])*` e registrá-las no Histórico como "Redação intermediária (substituída)". Proposta incluída no README.
- 2026-09-27, CONAMA 430/2011 × 357/2005: revogação parcial feita por norma que está na base. Fazer: como no Decreto 12.799/2026, a norma nova vai em `altera` (não em `revoga`), e a afetada recebe `alterado_por`, com os dispositivos tachados e `#revogado`.

## Validação

## Habilidades do claude.ai (ajustes pendentes)

Ajustes sugeridos para as habilidades que ficam fora do repositório. Remova o item quando o usuário aplicar a mudança.

- 2026-09-27, `base-legislacao`, seção 1 (Extrair o texto): acrescentar "Na nuvem, instale antes: `apt-get install -y poppler-utils` e `pip install pymupdf`. Em textos compilados (Planalto, CONAMA), detecte o tachado com PyMuPDF, porque o `pdftotext` o perde."
- 2026-09-27, `base-legislacao`, seção 5 (Revisão e commit): o texto manda usar o ramo `norma/<arquivo>`, mas as sessões na nuvem recebem um ramo designado e não podem publicar em outro sem autorização. Texto sugerido: "Faça o commit e o push no ramo `norma/<arquivo>` ou, numa sessão na nuvem, no ramo designado pela sessão. Nunca vá direto para o `main`."
- 2026-09-27, `base-legislacao`: não trata de documentos interpretativos (versões comentadas). Texto sugerido, nova seção "2B. Comentários oficiais": "Se Leo enviar uma versão comentada ou nota interpretativa oficial da norma, siga a seção 'Comentários oficiais' do README: arquivo próprio em `normas/comentarios/<arquivo>-coment.md`, um comentário por dispositivo com ID `<id-do-dispositivo>_coment` e link direto para o dispositivo, e link '(comentário)' de volta no dispositivo da norma."
- 2026-09-27, `base-legislacao`, seção 2A (Anexos, tipo 3): acrescentar "Tabelas no corpo de um artigo seguem o tipo 3, com ID `artN_tabT_linM`."
