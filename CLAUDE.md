# Instruções para o agente

Antes de converter ou atualizar qualquer norma, leia o README.md: ele define o padrão (nomes, IDs LexML, links, tags e o tratamento de alterações e revogações).

Regras principais:
- Nunca apague o arquivo de uma norma alterada ou revogada. Atualize-o como texto compilado.
- Transcreva o texto exatamente como publicado e registre os erros do original em "Notas de transcrição".
- Rode `python scripts/validar.py` e só faça commit com 0 erros.
- Mostre as mudanças ao usuário antes do commit e sinalize revogação tácita, remissões erradas e vigência diferida.
- Mensagem de commit: `norma: <arquivo> (nova | altera <arquivo> | revoga <arquivo>)`.
