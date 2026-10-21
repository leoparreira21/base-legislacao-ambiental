# Graph Report - base-legislacao-ambiental  (2026-10-20)

## Corpus Check
- Large corpus: 188 files · ~1,499,184 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 607 nodes · 4472 edges · 9 communities
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 696 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Licenciamento IAT e documentação
- Resíduos sólidos e logística reversa
- Recursos hídricos e padrões de qualidade
- Enquadramento de atividades (CNAE, porte)
- Fiscalização, sanções e agropecuária
- Competências e áreas protegidas
- Código Florestal e Mata Atlântica
- Política ambiental e obrigações gerais
- Emissões atmosféricas

## God Nodes (most connected - your core abstractions)
1. `Decreto Estadual nº 9.541/2025` - 202 edges
2. `Instrução Normativa IAT nº 28/2025` - 195 edges
3. `Instrução Normativa IAT nº 65/2025` - 183 edges
4. `Instrução Normativa IAT nº 41/2025` - 169 edges
5. `Instrução Normativa IAT nº 32/2025` - 163 edges
6. `Lei Estadual nº 22.252/2024` - 152 edges
7. `Instrução Normativa IAT nº 33/2025` - 150 edges
8. `Instrução Normativa IAT nº 25/2025` - 130 edges
9. `Instrução Normativa IAT nº 24/2026` - 129 edges
10. `Instrução Normativa IAT nº 31/2025` - 122 edges

## Surprising Connections (you probably didn't know these)
- `Contexto: Gestão de resíduos sólidos (ciclo e destinação)` --predomina_em--> `Categoria: Específicas para enquadramento`  [INFERRED]
  tags.md → _site/dispositivos.json
- `Contexto: Áreas sensíveis e restrições locacionais` --predomina_em--> `Categoria: Específicas para enquadramento`  [INFERRED]
  tags.md → _site/dispositivos.json
- `Contexto: Regime florestal rural (PRA, manejo, uso alternativo)` --predomina_em--> `Categoria: Específicas para enquadramento`  [INFERRED]
  tags.md → _site/dispositivos.json
- `Instrução Normativa IAT nº 24/2026` --enquadrada_em--> `Categoria: Específicas para enquadramento`  [INFERRED]
  normas/instrucao-normativa-iat-24-2026.md → _site/dispositivos.json
- `Instrução Normativa IAT nº 26/2026` --enquadrada_em--> `Categoria: Específicas para enquadramento`  [INFERRED]
  normas/instrucao-normativa-iat-26-2026.md → _site/dispositivos.json

## Hyperedges (group relationships)
- **Normas no contexto Gestão de resíduos sólidos (ciclo e destinação)** — norma_lei-federal-12305-2010, norma_decreto-estadual-6674-2002, norma_lei-estadual-12493-1999, norma_rdc-anvisa-222-2018, norma_resolucao-conama-358-2005, norma_instrucao-normativa-iat-28-2025, norma_decreto-federal-10936-2022, norma_instrucao-normativa-iat-32-2025 [INFERRED 0.70]
- **Normas no contexto Documentação fundiária e cadastros (CAR, CTF, outorga)** — norma_instrucao-normativa-iat-32-2025, norma_instrucao-normativa-iat-33-2025, norma_instrucao-normativa-iat-41-2025, norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-30-2025, norma_instrucao-normativa-iat-31-2025, norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-25-2025, norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-65-2025, norma_instrucao-normativa-iat-22-2026, norma_instrucao-normativa-iat-23-2026, norma_instrucao-normativa-iat-27-2026, norma_instrucao-normativa-iat-38-2025, norma_lei-federal-15190-2025, norma_instrucao-normativa-iat-6-2026, norma_instrucao-normativa-iat-21-2025 [INFERRED 0.70]
- **Normas no contexto Áreas sensíveis e restrições locacionais** — norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-65-2025, norma_lei-federal-15190-2025, norma_lei-estadual-22252-2024, norma_lei-complementar-federal-140-2011, norma_lei-federal-12651-2012, norma_instrucao-normativa-iat-32-2025, norma_lei-federal-6938-1981, norma_instrucao-normativa-iat-11-2026, norma_instrucao-normativa-iat-6-2026, norma_lei-federal-9985-2000, norma_resolucao-conama-237-1997 [INFERRED 0.70]
- **Normas no contexto Modalidades e etapas de licença (LP, LI, LO, LAS)** — norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-65-2025, norma_instrucao-normativa-iat-22-2026, norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-27-2026, norma_instrucao-normativa-iat-25-2025, norma_lei-estadual-22252-2024, norma_instrucao-normativa-iat-23-2026, norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-41-2025, norma_instrucao-normativa-iat-32-2025, norma_instrucao-normativa-iat-30-2025, norma_instrucao-normativa-iat-31-2025, norma_instrucao-normativa-iat-33-2025, norma_instrucao-normativa-iat-38-2025, norma_instrucao-normativa-iat-21-2025, norma_lei-federal-15190-2025, norma_instrucao-normativa-iat-9-2026, norma_portaria-iap-26-2006, norma_resolucao-conama-237-1997 [INFERRED 0.70]
- **Normas no contexto Monitoramento, impacto e medidas mitigadoras** — norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-41-2025, norma_lei-estadual-22252-2024, norma_resolucao-sedest-2-2025, norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-11-2026, norma_instrucao-normativa-iat-65-2025, norma_lei-federal-15190-2025, norma_resolucao-conama-382-2006 [INFERRED 0.70]
- **Normas no contexto Aterros e infraestrutura de disposição** — norma_instrucao-normativa-iat-32-2025, norma_instrucao-normativa-iat-33-2025, norma_instrucao-normativa-iat-30-2025, norma_instrucao-normativa-iat-31-2025, norma_instrucao-normativa-iat-41-2025, norma_resolucao-conama-358-2005, norma_instrucao-normativa-iat-28-2025, norma_lei-federal-12305-2010, norma_decreto-federal-10936-2022, norma_instrucao-normativa-iat-24-2026 [INFERRED 0.70]
- **Normas no contexto Atividades industriais e fontes poluidoras** — norma_instrucao-normativa-iat-11-2026, norma_instrucao-normativa-iat-65-2025, norma_instrucao-normativa-ibama-13-2021, norma_lei-federal-6938-1981, norma_resolucao-conama-237-1997, norma_instrucao-normativa-iat-29-2026, norma_instrucao-normativa-ibama-13-2012, norma_resolucao-conama-382-2006, norma_instrucao-normativa-iat-28-2025 [INFERRED 0.70]
- **Normas no contexto Requerimento e documentos do processo** — norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-65-2025, norma_instrucao-normativa-iat-25-2025, norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-41-2025, norma_instrucao-normativa-iat-22-2026, norma_instrucao-normativa-iat-32-2025 [INFERRED 0.70]
- **Normas no contexto Padrões de qualidade e de lançamento** — norma_resolucao-conama-357-2005, norma_resolucao-conama-396-2008, norma_instrucao-normativa-iat-28-2025, norma_resolucao-cerh-122-2023, norma_resolucao-conama-430-2011, norma_instrucao-normativa-iat-41-2025, norma_resolucao-sedest-2-2025 [INFERRED 0.70]
- **Normas no contexto Infrações, sanções e responsabilidade** — norma_decreto-estadual-9541-2025, norma_lei-estadual-22252-2024, norma_lei-federal-6938-1981, norma_lei-federal-15190-2025, norma_lei-federal-9605-1998, norma_resolucao-conama-358-2005, norma_instrucao-normativa-iat-11-2026, norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-65-2025, norma_instrucao-normativa-ibama-13-2021, norma_lei-federal-12305-2010, norma_instrucao-normativa-iat-38-2025, norma_instrucao-normativa-iat-41-2025, norma_instrucao-normativa-iat-6-2026, norma_lei-estadual-12493-1999, norma_resolucao-conama-357-2005 [INFERRED 0.70]
- **Normas no contexto Agropecuária, efluentes no solo e áreas contaminadas** — norma_instrucao-normativa-iat-23-2026, norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-26-2026, norma_resolucao-conama-430-2011, norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-11-2026, norma_instrucao-normativa-iat-29-2026, norma_instrucao-normativa-iat-41-2025, norma_instrucao-normativa-iat-65-2025, norma_lei-federal-12651-2012, norma_resolucao-conama-357-2005 [INFERRED 0.70]
- **Normas no contexto Gestão de recursos hídricos (SEGRH)** — norma_lei-estadual-12726-1999, norma_decreto-estadual-9957-2014, norma_lei-federal-9433-1997, norma_resolucao-cerh-122-2023 [INFERRED 0.70]
- **Normas no contexto Empreendimentos imobiliários e saneamento** — norma_instrucao-normativa-iat-21-2025, norma_instrucao-normativa-iat-31-2025, norma_instrucao-normativa-iat-32-2025, norma_instrucao-normativa-iat-30-2025, norma_instrucao-normativa-iat-33-2025, norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-28-2025, norma_instrucao-normativa-iat-41-2025 [INFERRED 0.70]
- **Normas no contexto Aptidão do solo, irrigação e aquicultura** — norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-22-2026, norma_instrucao-normativa-iat-26-2026, norma_instrucao-normativa-iat-27-2026, norma_instrucao-normativa-iat-65-2025, norma_instrucao-normativa-iat-33-2025, norma_instrucao-normativa-iat-41-2025, norma_lei-estadual-12726-1999, norma_lei-federal-12651-2012, norma_resolucao-cerh-122-2023, norma_resolucao-conama-357-2005 [INFERRED 0.70]
- **Normas no contexto Rito de licenciamento e insumos orgânicos** — norma_instrucao-normativa-iat-41-2025, norma_instrucao-normativa-iat-65-2025, norma_decreto-estadual-9541-2025, norma_instrucao-normativa-iat-24-2026, norma_instrucao-normativa-iat-25-2025, norma_instrucao-normativa-iat-28-2025, norma_lei-estadual-22252-2024, norma_lei-federal-15190-2025 [INFERRED 0.70]

## Communities (9 total, 0 thin omitted)

### Community 0 - "Licenciamento IAT e documentação"
Cohesion: 0.10
Nodes (146): Categoria: Específicas para licenciamento, Contexto: Documentação fundiária e cadastros (CAR, CTF, outorga), Contexto: Modalidades e etapas de licença (LP, LI, LO, LAS), Contexto: Aterros e infraestrutura de disposição, Contexto: Requerimento e documentos do processo, Contexto: Empreendimentos imobiliários e saneamento, Instrução Normativa IAT nº 21/2025, Instrução Normativa IAT nº 22/2026 (+138 more)

### Community 1 - "Resíduos sólidos e logística reversa"
Cohesion: 0.06
Nodes (107): Contexto: Gestão de resíduos sólidos (ciclo e destinação), Contexto: Resíduos químicos (Grupo B) e aterro classe I, Decreto Estadual nº 6.674/2002, Decreto Federal nº 10.936/2022, Instrução Normativa IBAMA nº 13/2012, Lei Estadual nº 12.493/1999, Lei Estadual nº 20.607/2021, Lei Federal nº 12.305/2010 (+99 more)

### Community 2 - "Recursos hídricos e padrões de qualidade"
Cohesion: 0.07
Nodes (86): Categoria: Limites de parâmetros, Contexto: Padrões de qualidade e de lançamento, Contexto: Gestão de recursos hídricos (SEGRH), Contexto: Áreas de influência e mananciais, Decreto Estadual nº 9.957/2014, Instrução Normativa IAT nº 29/2026, Instrução Normativa IAT nº 09/2026, Lei Estadual nº 12.726/1999 (+78 more)

### Community 3 - "Enquadramento de atividades (CNAE, porte)"
Cohesion: 0.07
Nodes (70): Categoria: Específicas para enquadramento, Contexto: Atividades industriais e fontes poluidoras, Contexto: Aptidão do solo, irrigação e aquicultura, Contexto: Rito de licenciamento e insumos orgânicos, Instrução Normativa IAT nº 11/2026, Instrução Normativa IAT nº 65/2025, Instrução Normativa IBAMA nº 13/2021, Resolução CONAMA nº 237/1997 (+62 more)

### Community 4 - "Fiscalização, sanções e agropecuária"
Cohesion: 0.07
Nodes (67): Contexto: Infrações, sanções e responsabilidade, Contexto: Agropecuária, efluentes no solo e áreas contaminadas, Decreto Estadual nº 9.541/2025, Instrução Normativa IAT nº 26/2026, Instrução Normativa IAT nº 06/2026, Lei Estadual nº 22.252/2024, Lei Federal nº 9.605/1998, Resolução SEDEST nº 39/2024 (+59 more)

### Community 5 - "Competências e áreas protegidas"
Cohesion: 0.10
Nodes (41): Contexto: Áreas sensíveis e restrições locacionais, Lei Complementar Federal nº 140/2011, Lei Federal nº 15.190/2025, Lei Federal nº 15.300/2025, Lei Federal nº 9.985/2000, #analise-risco, #apa, #aprovacao-tacita (+33 more)

### Community 6 - "Código Florestal e Mata Atlântica"
Cohesion: 0.12
Nodes (36): Contexto: Regime florestal rural (PRA, manejo, uso alternativo), Lei Federal nº 11.428/2006, Lei Federal nº 12.651/2012, Portaria IAT nº 354/2020, #agricultura-familiar, #area-rural-consolidada, #area-verde-urbana, #assentamento (+28 more)

### Community 7 - "Política ambiental e obrigações gerais"
Cohesion: 0.14
Nodes (30): Categoria: Normas gerais, Categoria: Obrigações e proibições, Decreto Estadual nº 12.799/2026, Instrução Normativa IAT nº 25/2026, Instrução Normativa IAT nº 28/2026, Instrução Normativa IAT nº 37/2025, Instrução Normativa IBAMA nº 23/2025, Lei Estadual nº 16.346/2009 (+22 more)

### Community 8 - "Emissões atmosféricas"
Cohesion: 0.16
Nodes (24): Contexto: Monitoramento, impacto e medidas mitigadoras, Resolução CONAMA nº 382/2006, Resolução SEDEST nº 02/2025, #amostragem, #caldeira, #chumbo, #cimento, #combustivel (+16 more)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Decreto Estadual nº 9.541/2025` connect `Fiscalização, sanções e agropecuária` to `Licenciamento IAT e documentação`, `Resíduos sólidos e logística reversa`, `Recursos hídricos e padrões de qualidade`, `Enquadramento de atividades (CNAE, porte)`, `Competências e áreas protegidas`, `Código Florestal e Mata Atlântica`, `Política ambiental e obrigações gerais`, `Emissões atmosféricas`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `Instrução Normativa IAT nº 28/2025` connect `Licenciamento IAT e documentação` to `Resíduos sólidos e logística reversa`, `Recursos hídricos e padrões de qualidade`, `Enquadramento de atividades (CNAE, porte)`, `Fiscalização, sanções e agropecuária`, `Competências e áreas protegidas`, `Código Florestal e Mata Atlântica`, `Política ambiental e obrigações gerais`, `Emissões atmosféricas`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `Instrução Normativa IAT nº 65/2025` connect `Enquadramento de atividades (CNAE, porte)` to `Licenciamento IAT e documentação`, `Resíduos sólidos e logística reversa`, `Recursos hídricos e padrões de qualidade`, `Fiscalização, sanções e agropecuária`, `Competências e áreas protegidas`, `Código Florestal e Mata Atlântica`, `Política ambiental e obrigações gerais`, `Emissões atmosféricas`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Decreto Estadual nº 9.541/2025` (e.g. with `Categoria: Específicas para licenciamento` and `Categoria: Normas gerais`) actually correct?**
  _`Decreto Estadual nº 9.541/2025` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Instrução Normativa IAT nº 28/2025` (e.g. with `Categoria: Específicas para licenciamento` and `Categoria: Normas gerais`) actually correct?**
  _`Instrução Normativa IAT nº 28/2025` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Instrução Normativa IAT nº 65/2025` (e.g. with `Categoria: Normas gerais` and `Categoria: Obrigações e proibições`) actually correct?**
  _`Instrução Normativa IAT nº 65/2025` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Instrução Normativa IAT nº 41/2025` (e.g. with `Categoria: Normas gerais` and `Categoria: Obrigações e proibições`) actually correct?**
  _`Instrução Normativa IAT nº 41/2025` has 13 INFERRED edges - model-reasoned connections that need verification._