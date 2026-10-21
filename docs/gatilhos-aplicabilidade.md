# Gatilhos de aplicabilidade

Resposta à pendência da [auditoria de 05/10/2026](auditoria/2026-10-05.md): "anotação estruturada de gatilhos de aplicabilidade com curadoria". Esta é uma versão piloto, feita sobre o caso de referência do ambulatório em renovação de LO e os dispositivos já citados nas auditorias.

## O que é um gatilho

Um gatilho é uma condição de fato que o próprio texto do dispositivo exige para que o comando incida. Exemplo: o art. 81 da RDC 222/2018 trata do "lançamento de rejeitos líquidos em rede coletora de esgotos, conectada à estação de tratamento". Ele só incide se o efluente vai para a rede coletora e se a rede está conectada à ETE.

Os gatilhos ficam em `consultas/gatilhos.json`, separados da transcrição. São metadados editoriais. Não alteram o texto da norma e não certificam vigência.

Cada condição tem um destes dois tipos:

- **campo**: compara um campo fechado do formulário do caso (`modalidade`, `agua`, `efluentes`, `localizacao`) com os valores de `OPCOES_CASO` (`site/motor.js`) que satisfazem a condição.
- **fato**: descreve um fato que o formulário não captura, como "utiliza reveladores em radiologia". O servidor nunca confirma um fato sozinho.

Toda condição cita um `trecho` literal. O build procura esse trecho no dispositivo, nos ancestrais dele ou no dispositivo indicado em `em` (da mesma norma). Use `em` quando a condição vem de um título de lista sem hierarquia de ID, como o item 5.1, VI, da IN 003/2006 anexa à Portaria IAP 26/2006. Os filhos herdam os gatilhos dos ancestrais. Assim, uma condição do caput também limita os incisos dele.

## Garantias do build

`scripts/gatilhos.py` é executado por `gerar_grafo.py`:

- ID inexistente, dispositivo inelegível (revogado ou editorial), campo desconhecido ou trecho que não está na norma interrompem o build.
- `texto_sha256` amarra a curadoria à redação. Se a redação mudar, o gatilho é ignorado com aviso, até nova curadoria. O teste `test_acervo_sem_gatilho_desatualizado_e_fatias` falha nesse caso.
- `testes/gatilhos.test.mjs` confere que todo valor curado existe no formulário e não é uma opção "Não informado".

## Uso no assistente

O Worker avalia cada condição contra os campos do caso (`avaliarGatilhos` em `recuperacao.mjs`):

| Estado | Quando |
|---|---|
| `atendida` | o campo tem um dos valores da condição |
| `nao_informada` | o campo está vazio ou na opção "Não informado" |
| `nao_atendida` | o caso informa outro valor: o fato contradiz o pressuposto do dispositivo |
| `a_confirmar` | condição de fato; sempre pendente de conferência |

As condições avaliadas vão para a IA junto com a evidência. O servidor também aplica uma regra própria: um item só sai como `aplicavel` se todas as condições estiverem atendidas. Caso contrário, `aplicavel` passa a `condicionada`. O servidor nunca promove uma classificação. A resposta publica as condições em `condicoes`, e o chat as mostra em cada cartão com o trecho de origem.

## Curadoria do piloto

23 dispositivos: RDC 222/2018 (arts. 5º, §§ 1º e 2º; 66; 67; 71; 81 e parágrafo único), CONAMA 430/2011 (art. 1º, parágrafo único; art. 2º), Portaria IAP 26/2006 (item 5.1, VI, alíneas a–i da IN 003/2006 anexa), Decreto 9.541/2025 (art. 121, § 4º; art. 124) e IN IAT 29/2026 (arts. 15, 16 e 18). Todos foram lidos no acervo antes da anotação. Não houve revisão jurídica externa.

Limites:

- A cobertura é pequena. A ausência de gatilho não significa que o dispositivo seja incondicional.
- Porte, CNAE e município não são campos fechados do formulário. Condições sobre eles entram como fato.
- A busca livre e a análise de caso sem IA (`index.html`) ainda não exibem os gatilhos.
- O pacote enviado à IA depende da seleção de evidências. No caso de auditoria do ambulatório, entram hoje os gatilhos do Decreto 9.541, art. 124, e da CONAMA 430, arts. 1º e 2º. A CONAMA 430, art. 2º, sai `nao_atendida`, porque o caso declara rede coletora.

## Como acrescentar um gatilho

1. Leia o dispositivo e os ancestrais no arquivo da norma.
2. Escreva a condição com um trecho copiado do texto. Para campo, use só valores de `OPCOES_CASO`.
3. Rode `python scripts/gatilhos.py norma#id` para obter o `texto_sha256`.
4. Rode `python scripts/gerar_site.py`, `python -m unittest testes.test_gatilhos` e `node --test testes/gatilhos.test.mjs`.
