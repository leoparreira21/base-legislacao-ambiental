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

A identidade oficial AmbLegis está nos tokens `--brand-*` de `src/index.css`. A logo
em uso fica em `src/assets/amblegis-logo-512.png` (512×512, RGBA com transparência real)
e é incorporada no HTML pelo import
`data-url:` do Parcel, sem depender de um arquivo remoto. As páginas do leitor usam
a mesma paleta no CSS de `scripts/gerar_html.py`. Os temas acompanham a preferência
do sistema. A logo aparece inteira a 64×64 ao lado do título, sem fundo opaco ou bloco
exclusivo acima dos filtros; o JPEG anterior permanece como fonte histórica.
No tema escuro, um filtro CSS usa a apresentação monocromática branca, preservando
o arquivo colorido e garantindo que os detalhes não sumam sobre o fundo azul.

No Windows, com as dependências já instaladas, os comandos diretos equivalentes são:

```powershell
node node_modules/parcel/lib/bin.js build index.html --dist-dir dist --no-source-maps --no-autoinstall
node node_modules/html-inline/bin/cmd.js dist/index.html > ../site/biblioteca.html
```

Onde abrir:
- publicada no Cloudflare (`biblioteca-legislacao-ambiental`): o `scripts/montar_biblioteca.py` copia a página, gera `html/` e as imagens dos anexos;
- no repositório: abrir `site/biblioteca.html` direto no navegador (procura `../html/`).

A faixa "Consulta no texto" (`src/ConsultaSQL.tsx`) chama `/api/buscar` do Worker `cloudflare/biblioteca/worker.mjs` (D1). Ela só aparece quando `/api` responde: coluna à direita a partir de 1280 px de largura, painel sobreposto (botão "Consulta no texto dos dispositivos") nas telas menores.

No modo Avançado, uma fileira de botões (`OR`, `AND`, `NOT`, `NEAR( , 10)`, aspas e `*`) abaixo do campo
insere o operador no cursor; aspas e `NEAR` envolvem o trecho selecionado. No modo Simples ela não aparece.
Na lista de normas, esfera e situação são duas listas de seleção numa linha; os tipos continuam como botões.

Os cartões mostram o nome, a contagem de dispositivos e a súmula do catálogo (com a
ementa da API como alternativa). Os trechos ficam apenas em "Ver os N dispositivos",
inclusive quando há uma única ocorrência. `RotuloDispositivo.tsx` abrevia as referências
sem mudar os IDs ou o texto da norma: `Art. 8º, VII, h`, com a letra da alínea em itálico.

Abrir um resultado ativa o localizador no leitor: anterior/próxima ocorrência, contador,
F3/Shift+F3 e Esc para fechar. Ele percorre **dispositivos**, na ordem do documento,
usando a mesma consulta e os mesmos filtros da busca; não conta repetições da palavra
dentro do dispositivo. Abre somente os caminhos dos dispositivos encontrados e restaura
a expansão anterior ao fechar. O atributo temporário `data-localizar-ocorrencias` impede
que o controlador de `gerar_html.py` expanda os irmãos ao abrir um artigo nesse modo.
Consultas atrasadas são canceladas; falha na carga dos dispositivos permite tentar novamente.
A lista por norma percorre a continuação `proximo_offset` da API, em lotes de até
1.000 dispositivos; o localizador não fica limitado ao primeiro lote.

Verificação do fluxo (Chromium e pacote Python `playwright`):

```bash
python scripts/montar_biblioteca.py _biblioteca
python testes/biblioteca_ui.py
```

Os testes usam as páginas reais geradas e respostas simuladas, sem consultar D1 ou IA.

Consulta simples e avançada (27/11/2026): o seletor "Simples | Avançada" manda `modo=simples|avancado`
para `/api/buscar`. Na simples o Worker tira acentos e monta `termo OR plural OR "frase"`; na avançada a
expressão vai ao FTS5 como foi escrita (AND, OR, NOT, NEAR, aspas, `*`, parênteses). Os filtros (tipo de
norma, esfera, ano, tipo de dispositivo, ocultar revogados) vão ao D1 como `tipo_norma`, `esfera`, `ano`,
`tipo` e `ocultar_revogados`; as opções vêm de `/api/filtros`, com os nomes que estão no D1. O destaque usa
os `termos` devolvidos pela API. Lista da norma e localizador repetem o mesmo modo e os mesmos filtros.
