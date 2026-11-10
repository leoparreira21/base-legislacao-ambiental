# Validação da continuidade — 08/11/2026

- Base de comparação: `88429355072d0661d344d1ae5ba1aa00d0e2e437`.
- Integridade dos 52 arquivos de normas/anexos modificados: texto fora das tags, IDs, wikilinks e marcadores de controle preservados.
- `python scripts/validar.py`: 183 documentos, zero erros, 153 avisos de referências fora do acervo.
- `python scripts/auditar_taxonomia_tags.py`: 819 tags cobertas, sem ciclos, aliases válidos.
- `python scripts/integrar_revisao_tags.py`: 1.364 decisões, zero divergências entre decisões e tags atuais; 80 grupos de identidade textual com 139 ocorrências adicionais para conferência.
- `python -m unittest discover -s testes -v`: 61 testes aprovados em 124,759 s.
- `python scripts/auditar_consultas.py`: 22 cenários; 67/67 evidências esperadas na consulta expandida.
- `python scripts/gerar_html.py`: páginas regeneradas, sem mudança versionada.
- `python scripts/gerar_site.py` e `python scripts/validar_indices.py`: 43.382 identificadores, 42.819 arestas, 3.963 referências pendentes, 183 fatias; zero erros.
- `git diff --check`: sem erros.

Os testes do integrador verificam preservação de limites e remissões na detecção de duplicatas, rejeição de decisão divergente e ausência de replicação automática de decisões. Não são testes de correção jurídica ou de respostas de um agente de IA. O Graphify remoto não foi usado para indexação: a conexão retornou lista vazia de workspaces.
