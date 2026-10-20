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
