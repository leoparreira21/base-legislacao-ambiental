# Direção de design

## North Star
Mesa de consulta técnica: do fato informado ao dispositivo verificável. Público: profissionais de licenciamento ambiental no Paraná, em português brasileiro, no computador e celular.

## Referências e limites
Preservar a identidade das fichas de normas existentes. Sem chat que pareça dar parecer definitivo; nenhuma porcentagem de confiança sem calibração. A assinatura visual é o dispositivo em ficha com citação conferível, ao lado dos dados que determinam seu enquadramento.

## Tokens e tipografia
Fonte canônica: `site/estilo.css`, compartilhada com a busca existente. Fundo #f3f5f4, superfície #ffffff, texto #1d2621, secundário #5b6a62, borda #d6dfda, ação #1f5f8b. O tema escuro segue os mesmos tokens existentes. Source Serif 4 para títulos/dispositivos, IBM Plex Sans para leitura, IBM Plex Mono para referências. Fontes do sistema como fallback.

## Layout
`site/assistente.css`: duas colunas (caso e conversa), uma coluna abaixo de 700px; dados recolhíveis no celular. Sem overlay flutuante que esconda citações. Rolagem do documento, texto longo quebra, inputs editáveis e área de texto cresce até 300px.

## Interações
`site/assistente.js` é o controlador da conversa, `site/motor.js` mantém opções canônicas, `site/estilo.css` mantém botões e campos. Selects nativos: popup do sistema operacional é intencional. Status persistente, erro junto ao composer, cancelamento, proteção contra resposta atrasada e envio duplicado. Mensagens sem persistência em URL/localStorage; o caso pode conter informação de processo. Novo caso com restauração reversível. Fontes são links seguros, nunca HTML vindo da IA.

## Acessibilidade
Idioma pt-BR, labels explícitos, foco visível, teclado nativo, status/erro anunciados, aba de busca com setas e Home/End, reduced motion. Alterações não declaram conformidade WCAG auditada integralmente.

## Verificação
Testes Node de contrato, seleção, entradas, limites, falhas, integração com acervo real; Playwright quando disponível. Ver `auditorias/2026-10-20-assistente.md` para evidências e limitações.
