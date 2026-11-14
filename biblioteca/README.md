# Biblioteca de normas (código-fonte)

Fonte da página `site/biblioteca.html`: lista das normas com busca e filtros (esfera, situação, tipo) e leitor das páginas de `html/`.
React + TypeScript + Tailwind/shadcn, empacotado num único HTML.

A lista vem de `html/catalogo.js`, gerado por `python scripts/gerar_html.py` a partir do frontmatter das normas.
Norma nova entra na biblioteca sem recompilar nada: basta regerar `html/`.

Só recompile quando mudar a própria biblioteca:

```bash
cd biblioteca
pnpm install
pnpm exec parcel build index.html --dist-dir dist --no-source-maps
pnpm exec html-inline dist/index.html > ../site/biblioteca.html
```

(O empacotamento usado foi o `bundle-artifact.sh` da habilidade web-artifacts-builder, que faz os mesmos passos.)

Onde abrir:
- site publicado: `/biblioteca.html` (o `gerar_site.py` copia a página, gera `html/` e as imagens dos anexos);
- no repositório: abrir `site/biblioteca.html` direto no navegador (procura `../html/`).

A faixa "Consulta no texto" (`src/ConsultaSQL.tsx`) chama `/api/buscar` do Worker `cloudflare/biblioteca/worker.mjs` (D1). Ela só aparece quando `/api` responde: coluna à direita a partir de 1280 px de largura, painel sobreposto (botão "Consulta no texto dos dispositivos") nas telas menores.
