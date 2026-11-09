# Conversor de textos compilados (Planalto e Câmara)

Gera o Markdown da base a partir das impressões em PDF do Planalto (texto compilado, com ou sem tachado) e do texto atualizado da Câmara. Usado na leva de 09/11/2026 (CF/1988, CPC/2015, CPC/1973, Leis 4.771/1965, 8.847/1994, 11.326/2006 e 11.977/2009); cada norma tem um `cfg_*.py`.

```
mkdir trab && cd trab && mkdir pdf          # pasta de trabalho fora do repositório
cp <pdf> pdf/cf.pdf
python ../scripts/conversor_planalto/extract.py pdf/cf.pdf cf.json            # Planalto (PyMuPDF)
pdftotext -layout pdf/l11977.pdf pdf/l11977.lay.txt
python ../scripts/conversor_planalto/extract_camara.py pdf/l11977.lay.txt l11977.json   # Câmara
CONV_TRAB=$PWD python ../scripts/conversor_planalto/cfg_cf.py                  # grava normas/<arquivo>.md
CONV_TRAB=$PWD python ../scripts/conversor_planalto/verify.py cfg_cf           # contagem de palavras PDF × Markdown
```

- `extract.py`: linhas pela linha de base (o "o" sobrescrito do ordinal vai para junto do número), parágrafo por espaço vertical e recuo, tachado pelos traços horizontais que cruzam o meio das palavras (`s` = fração tachada; `st` marca as palavras com `~`).
- `make.py`: descarta o tachado (redação anterior), mantém o rótulo de dispositivo revogado com a anotação "(Revogado ...)" que fica sem tachado, separa vários artigos num parágrafo, monta frontmatter (relações recíprocas lidas da base), fecho, assinaturas, relação, histórico e notas.
- `conv.py`: reconhecimento (Parte/Livro/Título/Capítulo/Seção/Subseção, Art., §, incisos, alíneas, itens, "Arts. N a M", blocos citados entre aspas), IDs LexML, anotações do Planalto e da Câmara, links para normas (`lei-federal-N-AAAA`, `emenda-constitucional-federal-N-AAAA`...) e links internos ao número do artigo.
- Ver `licoes.md` (09/11/2026) para as armadilhas tratadas.
