# Glossary — base-legislacao-ambiental

> Plain-English definitions of domain-specific terms used throughout this atlas. Alphabetical. Technical terms from the annexes live in the repo's own `glossario.md` (see [glossario-termos](glossario-termos/feature.md)).

### Term: Anexo tipo 1 / tipo 2 / tipo 3

The three ways an annex is handled. Type 1 (models: declarations, certificates) keeps only the model's name. Type 2 (study guidelines, terms of reference) goes to its own file in `normas/anexos/`. Type 3 (normative content, tables) is transcribed inline as one list entry per provision or table row. See [modelos-anexos](modelos-anexos/feature.md), [diretrizes-estudo-anexos](diretrizes-estudo-anexos/feature.md), [enquadramento-industrial](enquadramento-industrial/feature.md).

### Term: Dispositivo

Any addressable unit of a norma: article, caput, paragraph, inciso, alínea, item, or annex line. Every dispositivo gets a `{#id}` anchor.

### Term: IAT

Instituto Água e Terra, the PR state environmental agency that issues the Instruções Normativas (IN).

### Term: LexML ID

The anchor scheme for dispositivos, e.g. `art5_cpt_inc3_alia` or `anexo2_tab1_lin6`. Links target these IDs. See [consultar-dispositivo](consultar-dispositivo/feature.md).

### Term: Link pendente

A wiki link to a norma not yet in the base. It stays in place and starts working once a file with that name is added. The validator reports these as warnings, not errors.

### Term: Modalidade

A license type in PR licensing (e.g. LAS, LP, LI, LO, LAC and their ampliação/regularização/renovação variants). Type 2 annexes declare which modalidades require them.

### Term: Norma

One legal act (lei, decreto, instrução normativa, resolução). One Markdown file per norma under `normas/`.

### Term: Síntese do conversor

The second part of every type 2 annex file. It explains the study's content with sources, and is explicitly **not** normative text.

### Term: Texto compilado

The consolidated text of a norma after amendments: current wording in place, replaced or revoked wording kept struck through (`~~...~~`) with control tags. See [texto-compilado-alteracoes](texto-compilado-alteracoes/feature.md).
