# Validação do lote

- `python scripts/validar.py`: 183 documentos, zero erros, 153 avisos de referências fora da base.
- `python scripts/auditar_consultas.py`: 22 cenários; 67/67 evidências esperadas recuperadas pela consulta expandida. Não é benchmark independente ou avaliação de respostas de IA.
- `python -m unittest discover -s testes -v`: 55 testes existentes aprovados (112,527 s).
- `python -m unittest discover -s testes -p test_taxonomia_tags.py -v`: 3 novos testes aprovados.
- `python scripts/auditar_taxonomia_tags.py`: 819 tags cobertas, sem ciclos, aliases válidos.
- `python scripts/gerar_html.py`: 76 páginas, com 107 anexos integrados; sem diferença versionada.
- `python scripts/gerar_site.py` e `python scripts/validar_indices.py`: 43.382 identificadores, 42.819 arestas, 3.963 referências pendentes, 183 fatias, zero erros.
- `git diff --check`: sem erros.
- Comparação com commit-base: tokens do texto fora das tags, IDs, links e controles editoriais preservados nos quatro arquivos alterados. Metadados alterados somente em `tags`.

Essas verificações não certificam a correção semântica de todas as tags nem a vigência externa das normas. O motor atual não consome a proposta de hierarquia. Nenhum teste com agente de IA foi executado.
