---
version: alpha
colors:
  background: "#071511"
  surface: "#102820"
  text: "#edf8f2"
  muted: "#b0c8bc"
  border: "#416454"
  primary: "#82f5b5"
  case: "#7cddff"
  chat: "#c5adff"
  warning: "#ffd18a"
typography:
  display:
    fontFamily: "Space Grotesk, IBM Plex Sans, system-ui, sans-serif"
  body:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
  mono:
    fontFamily: "IBM Plex Mono, monospace"
rounded:
  control: "8px"
  card: "14px"
  hero: "20px"
spacing:
  panel: "24px"
  mobile: "16px"
omitted:
  - section: components
    reason: "Receitas canônicas em site/estilo.css e site/assistente.css."
---
# Observatório ambiental

## Biblioteca de normas (superfície independente)

A biblioteca publicada no Worker usa a identidade AmbLegis Database, aprovada pelo usuário
em 15/11/2026 a partir da logo e da paleta Color Designer. Mantém Georgia nos títulos e
fontes do sistema nos controles, com variante escura conforme a preferência do sistema.
Os tokens canônicos estão em `biblioteca/src/index.css` (`--brand-*` e tokens semânticos);
as páginas de leitura em `scripts/gerar_html.py` espelham essa identidade.

| Papel | Cor oficial | Uso |
|---|---|---|
| Azul institucional | #143154 | Texto principal e superfícies escuras |
| Verde araucária | #155442 | Ações com texto claro, links e títulos dos dispositivos |
| Verde ambiental | #179B38 | Faixa da marca |
| Verde-lima | #79AF22 | Ações na variante escura |
| Azul-petróleo | #258BA3 | Faixa da consulta no texto |
| Dourado | #C6A556 | Destaques com texto azul institucional |
| Cinza azulado | #C6D5DE | Bordas claras e texto secundário escuro |
| Branco suave | #F6F7F5 | Fundo claro e texto na variante escura |

As variações de superfície e texto secundário derivam dessa paleta para manter contraste.
Ações claras usam verde araucária; o verde ambiental fica nos detalhes, pois texto branco
pequeno sobre ele não oferece contraste suficiente. A logo oficial é o JPEG original em
`biblioteca/src/assets/amblegis-logo.jpeg`, incorporado no HTML; a apresentação corta apenas
margens vazias, preservando símbolo, nome e assinatura. No tema escuro mantém o fundo
original da imagem. A faixa verde identifica o catálogo e a azul identifica a consulta.
Scrollbars e foco usam os tokens compartilhados; alto contraste e redução de movimento
respeitam as preferências do sistema.
As regras noturnas do Observatório abaixo pertencem à busca e ao assistente, não a esta biblioteca.

Os resultados da consulta exibem súmula e contagem; os trechos são revelados por norma.
O localizador fica acima do documento, dentro da coluna do leitor, com controles que
quebram em linhas no celular. Usa os botões compartilhados, destaque do documento e
contorno para a ocorrência atual; a posição também é informada por contador textual.

## Overview
Ferramenta de consulta técnica para profissionais de licenciamento ambiental no Paraná. A direção aprovada em 20/10/2026 é ambiental e futurista: superfícies de floresta noturna, linhas topográficas e três ambientes cromáticos. A expressão visual aparece no cabeçalho e na navegação; a leitura dos dispositivos permanece sóbria. Não se apresenta como parecer definitivo nem usa porcentagens artificiais de confiança.

## Colors
Modelo B: o CSS de runtime é a fonte canônica. DESIGN.md espelha valores e explica seu uso; não gera CSS. Tema escuro deliberado em todos os ambientes, independente da preferência do sistema.

| Ambiente / seletor data-workspace | Fundo --bg | Superfície --surface | Secundário --muted | Borda --line | Ação --accent |
|---|---|---|---|---|---|
| livre | #071511 | #102820 | #b0c8bc | #416454 | #82f5b5 |
| caso | #07151e | #102a39 | #b3cbd9 | #42687d | #7cddff |
| chat | #101321 | #20253b | #c0c5df | #586384 | #c5adff |

Texto compartilhado --fg #edf8f2; texto de ação --accent-ink #071511; avisos --warn #ffd18a. Campos usam --field e chips usam --chip de cada ambiente. As cores de ambiente são expressivas, não significam validade jurídica. Rótulos e indicadores de seleção acompanham a cor.

## Typography
Space Grotesk para títulos e fichas; IBM Plex Sans para leitura; IBM Plex Mono para identificadores. Fallbacks locais mantêm funcionamento sem Google Fonts. Texto normativo 15px/1.75; campos 16px para evitar zoom automático no celular; título principal fluido 28–46px.

## Layout
Busca com largura máxima de 1140px. Chat até 1440px, caso em coluna de 330px e conversa flexível. Abaixo de 700px, coluna única e dados do caso recolhíveis. Navegação mostra os três ambientes; os dois primeiros são tabs e o terceiro é um link. Rolagem do documento, sem overlay sobre fontes. Conteúdo não depende de largura fixa.

## Elevation & Depth
Cards com bordas visíveis, faixa de cor e sombra discreta. Cabeçalho com linhas topográficas decorativas em CSS; ícone de folha SVG inline, sem requisições de imagens ou animação contínua. O fundo é mais escuro que campos e painéis.

## Shapes
Controles 8px; fichas 14px; cabeçalho 20px. Pill apenas para metadados e estado. Foco com outline explícito; modo de alto contraste mantém indicador de seleção.

## Components
| Papel | Fonte canônica | Consumidores |
|---|---|---|
| Cores / temas | site/estilo.css :root e data-workspace | Todas as superfícies |
| Tipografia | --f-display / --f-body / --f-mono | Títulos, leitura e referências |
| Botões / campos | .btn, .ghost, input, select, textarea | Busca, caso, chat |
| Navegação | .environment-nav, .tabs, .tool-nav | Três ambientes |
| Ficha de norma | .norma | Resultados livres e por eixo |
| Conversa / evidência | site/assistente.css | Chat |
| Comportamento | UX-CONTRACT.md | Controladores existentes |

Selects nativos, estados de carregamento/erro/cancelamento, retorno com fontes e restauração de caso preservados. Não se armazena a conversa em URL/localStorage.

## Do's and Don'ts
Manter títulos legíveis, texto longo com quebra e contraste alto. Não usar brilho sobre parágrafos, cor como único indicador, animações contínuas ou decoração que dificulte a consulta. Respeitar prefers-reduced-motion e teclado.

## Verificação
Build estático, testes de contrato e Playwright em 1440px e 390px. Verificação visual dos três ambientes, resultados e resposta com fonte. Mudança intencional autorizada pelo usuário: substituição da paleta clara/automática e títulos serifados por identidade ambiental noturna e tipografia geométrica.
