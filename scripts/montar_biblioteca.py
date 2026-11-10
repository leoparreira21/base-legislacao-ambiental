"""Monta a pasta da biblioteca publicada no Cloudflare (Worker com arquivos estáticos).

Uso: python scripts/montar_biblioteca.py [saida]   (padrão: _biblioteca)

Conteúdo: site/biblioteca.html como página inicial (e também como biblioteca.html),
as páginas de consulta de html/ regeradas a partir das normas e as imagens dos anexos,
que as páginas citam como ../normas/anexos/imagens/.
A configuração do Worker fica em cloudflare/biblioteca/wrangler.jsonc.
"""
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main():
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / '_biblioteca').resolve()
    if saida.exists():
        shutil.rmtree(saida)
    saida.mkdir(parents=True)
    pagina = RAIZ / 'site' / 'biblioteca.html'
    shutil.copy(pagina, saida / 'index.html')
    shutil.copy(pagina, saida / 'biblioteca.html')
    subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'gerar_html.py'), str(saida / 'html')], check=True)
    shutil.copytree(RAIZ / 'normas' / 'anexos' / 'imagens', saida / 'normas' / 'anexos' / 'imagens')
    arquivos = [p for p in saida.rglob('*') if p.is_file()]
    print(f'{len(arquivos)} arquivos em {saida}')


if __name__ == '__main__':
    main()
