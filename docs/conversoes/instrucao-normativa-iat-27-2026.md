# Conferência da IN IAT nº 27/2026

Conversão local concluída em 12/10/2026, no ramo `norma/instrucao-normativa-iat-27-2026`, sobre o SHA `655d6a66fa1b15c5be149b26940b2a89de9683d1` (HEAD e origin/main previamente buscados pelo usuário). Sem publicação remota.

## Fonte e arquivos

- Fonte recebida: `IN 27 2026.pdf`, localizada em `C:/Users/leo_p/Downloads/acrescentar à base legislação ambiental/já acrescentadas/IN 27 2026.pdf`; o caminho inicialmente indicado não existia mais.
- PDF eProtocolo nº 24.404.724-6, 83 páginas, assinatura em 19/08/2026. SHA256: `ac412780e3142df43d6f3ae6597f78a7a10a34473e77c6346cb612329b00ba9a`.
- Norma: [instrucao-normativa-iat-27-2026.md](../../normas/instrucao-normativa-iat-27-2026.md), 99 artigos, 769 dispositivos do corpo.
- Anexos técnicos separados: [V](../../normas/anexos/instrucao-normativa-iat-27-2026-anexo5.md) (18 disposições), [VI](../../normas/anexos/instrucao-normativa-iat-27-2026-anexo6.md) (10) e [VII](../../normas/anexos/instrucao-normativa-iat-27-2026-anexo7.md) (9), com transcrição e síntese identificadas separadamente.
- Na mãe: Anexo I (18 linhas de enquadramento, seis observações e três legendas), IV (seis disposições), VIII (seis linhas de frequência); modelos II, III, IX, X e XI representados pelo nome.
- Atualizados `consultas/ambitos.json`, `tags.md`, `glossario.md` (dois verbetes explicativos) e `licoes.md`.

## Efeitos e pontos de revisão

O art. 99 revoga a IN IAT nº 51/2025, ausente do acervo; registrada a relação, sem inventar transcrição. Não há arquivo preexistente de norma revogada/alterada a compilar. Entrada em vigor na publicação, cuja data/DIOE não constam do PDF; há aplicação aos processos em tramitação, com ressalva expressa do art. 173 do Decreto nº 9.541/2025.

As notas da norma registram o Decreto “9.514” no preâmbulo, a remissão à ART como inciso IV no art. 8º, § 2º, a numeração IV–XVIII do art. 48 e d–l do art. 54, inciso VI, a repetição dos arts. 89/91, as grafias publicadas e os intervalos numéricos dos quadros. O Quadro I menciona carcinicultura, apesar da exclusão do art. 1º, § 1º. Não foram corrigidos os limites ou o alcance das disposições.

Anexos VI e VII não têm chamada direta no corpo; o enquadramento contextual e essa limitação estão registrados nas sínteses. O parêntese “(mover para as listas dos documentos)” do Anexo V foi transcrito como conteúdo publicado; nenhuma instrução do PDF foi executada como pedido do usuário.

## Validação e recuperação

- `python scripts/validar.py`: 97 documentos (39 normas, 57 anexos, um comentário), zero erros e 88 avisos relativos a referências fora da base.
- `python scripts/validar.py --tags`: executado, catálogo atualizado.
- `python scripts/validar.py --afetados instrucao-normativa-iat-27-2026`: nenhuma outra norma aponta para dispositivos revogados/alterados desta IN.
- `git diff --check`: sem problemas de espaços.
- `python scripts/gerar_site.py`: site local gerado em `_site/` (ignorado pelo Git).
- Executadas as funções reais `construir`, `admite` e `buscar` de `site/index.html` em Node com o índice gerado: recuperadas a norma por aquicultura, piscicultura, maricultura, ranicultura e tanque rede e os três anexos. O âmbito não admite a norma pela busca “industria argamassa”.

### Comparação independente com o PDF

`difflib.SequenceMatcher` comparou a extração Poppler simples e com layout ao conteúdo efetivamente escrito no Markdown, recuperando os marcadores publicados dos rótulos LexML e o texto visível dos wikilinks, retirando IDs e tags e normalizando espaços. O corpo tem 19.679 palavras com marcadores restaurados. A extração simples perde sete hífens de SICAR-PR e o separador SAP/MAPA - SPU; a extração com layout parte as sete siglas SICAR-PR entre linhas. Após somente esses tratamentos, documentados e conferidos, há igualdade integral. Os anexos IV/V/VI/VII são idênticos sem ajustes de conteúdo. Tabelas dos anexos I/VIII foram conferidas nas imagens, com 18/seis linhas respectivamente.

### Referências pendentes da norma nova

instrucao-normativa-iat-27-2026: 35 norma(s) citada(s) fora da base: constituicao-federal-1988, decreto-estadual-11977-2022, decreto-estadual-13433-2026, decreto-estadual-2432-2019, decreto-estadual-3813-2020, decreto-estadual-8680-2013, decreto-estadual-9514-2025, decreto-estadual-9957-2014, decreto-federal-10576-2020, decreto-federal-6514-2008, instrucao-normativa-iat-51-2025, instrucao-normativa-iat-6-2023, instrucao-normativa-interministerial-seap-mma-mp-6-2004, lei-estadual-10066-1992, lei-estadual-12726-1999, lei-estadual-19848-2019, lei-estadual-20070-2019, lei-estadual-3919-1992, lei-federal-11959-2009, lei-federal-13288-2016, lei-federal-15190-2025, lei-federal-9605-1998, lei-federal-9984-2000, portaria-aguas-parana-46-2010, portaria-conjunta-sap-mapa-spu-seddm-me-396-2021, portaria-iap-256-2013, portaria-ibama-145-1998, portaria-sap-mapa-412-2021, resolucao-ana-188-2024, resolucao-cema-105-2019, resolucao-cerh-9-2020, resolucao-conama-312-2002, resolucao-conama-413-2009, resolucao-conama-459-2013, resolucao-conama-6-1986

Os 35 destinos ausentes continuam como wikilinks pendentes; não foram tratados como normas consultadas. Os anexos técnicos não acrescentam outros destinos ausentes. A lista de avisos globais inclui referências preexistentes das demais normas.
