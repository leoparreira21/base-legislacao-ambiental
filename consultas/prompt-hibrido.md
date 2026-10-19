# Complemento do prompt para a consulta híbrida (versão 1)

Este complemento deve ser usado com consultas/prompt-agente.md e não
substitui suas regras de fidelidade normativa, triagem e limites de aplicação.

## Entrada
O servidor fornecerá:
- dados do caso e campos desconhecidos;
- SHA do commit fixado para a consulta;
- candidatos recuperados pelo motor lexical;
- dispositivos.json e grafo.json já filtrados para um conjunto pequeno,
  incluindo pais, exceções, remissões e alterações pertinentes.

Não procure normas fora desse conjunto como se fossem fontes verificadas.
Se o conjunto for insuficiente, solicite outra recuperação ao servidor (quando
essa função existir) ou registre a lacuna; não complete com memória do modelo.
Não atribua a um wikilink a natureza de obrigação ou de revogação, salvo
quando esta estiver expressa em metadado tipado ou texto normativo.

## Procedimento
1. Compare os fatos efetivos do caso com hipóteses e exclusões do dispositivo.
2. Identifique exceções e condições nos parágrafos e anexos relacionados.
3. Selecione apenas dispositivos cujo conteúdo foi efetivamente recebido.
4. Classifique cada dispositivo:
   aplicavel / condicionada / contextual / nao_aplicavel.
5. Fundamente cada classificação em texto recebido, indicando insuficiência
   de dados quando a aplicação depender de informação desconhecida.
6. Mantenha notas interpretativas e comentários separados de obrigação legal.
7. Não certifique vigência externa: a situação é a cadastrada no snapshot.
8. Para regras quantitativas, compare unidades, limites e condições de
   incidência, sem extrapolar valores ausentes.

## Saída
Devolva somente um objeto JSON válido, sem Markdown, com:
- versao: consulta-hibrida/1
- commit: o SHA recebido
- itens: lista de:
  - chave: ID composto norma#dispositivo
  - classificacao: aplicavel, condicionada, contextual ou nao_aplicavel
  - fundamentacao: explicação vinculada aos fatos do caso
  - condicao: opcional quando a aplicação depende de fato não confirmado
  - evidencias: uma ou mais ocorrências {chave, trecho}, incluindo sempre
    o dispositivo principal; trecho literal contínuo do texto indexado
- lacunas: lista das informações não resolvidas.

O contrato completo está em consultas/contrato-resposta.schema.json.
Não invente chaves, normas, citações ou condições. Não use dispositivos
revogados nem seções interpretativas como fundamentos positivos. A validação
determinística checa IDs, SHA, elegibilidade e trecho literal, mas não julga
se a interpretação é juridicamente correta.
