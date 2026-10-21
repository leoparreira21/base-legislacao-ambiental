#!/usr/bin/env python3
"""Gatilhos de aplicabilidade curados: condições de fato que o próprio texto exige.

Cada condição cita um trecho literal da norma. O build confere o trecho e o hash da
redação; não infere condições nem decide aplicabilidade. A avaliação contra os
campos do caso é feita no Worker (cloudflare/legislacao-ambiental-api/recuperacao.mjs).

Uso: python scripts/gatilhos.py norma#id [...]  -> imprime texto_sha256 e texto limpo.
"""
import hashlib
import json
from pathlib import Path
import sys

from classificar_dispositivos import texto_limpo

FORMATO = 'gatilhos/1'
# Campos com valores fechados no formulário do caso (site/motor.js, OPCOES_CASO).
CAMPOS = ('modalidade', 'agua', 'efluentes', 'localizacao')


def _normal(texto):
    return ' '.join(texto_limpo(texto).split()).lower()


def _sha(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def _condicao(chave, c, norma, por_id):
    if not isinstance(c, dict) or ('campo' in c) == ('fato' in c):
        raise ValueError(f'{chave}: cada condição tem "campo" ou "fato", não ambos')
    extras = set(c) - {'campo', 'valores', 'fato', 'trecho', 'em'}
    if extras:
        raise ValueError(f'{chave}: campos desconhecidos {sorted(extras)}')
    if 'campo' in c:
        valores = c.get('valores')
        if (c['campo'] not in CAMPOS or not isinstance(valores, list) or not valores or
                len(set(valores)) != len(valores) or
                not all(isinstance(v, str) and v.strip() for v in valores)):
            raise ValueError(f'{chave}: campo/valores inválidos')
    elif not isinstance(c['fato'], str) or not 10 <= len(c['fato']) <= 300:
        raise ValueError(f'{chave}: fato deve ter de 10 a 300 caracteres')
    trecho = c.get('trecho')
    if not isinstance(trecho, str) or len(trecho.strip()) < 8:
        raise ValueError(f'{chave}: trecho literal obrigatório (8+ caracteres)')
    em = c.get('em')
    if em is not None and (em not in por_id or em.split('#')[0] != norma):
        raise ValueError(f'{chave}: "em" deve ser um dispositivo da mesma norma')


def aplicar(dispositivos, raiz):
    """Anexa `gatilhos` aos dispositivos elegíveis; filhos herdam os dos ancestrais.

    Retorna avisos de gatilhos ignorados porque a redação mudou desde a curadoria.
    Erros de curadoria (ID, campo ou trecho inexistente) interrompem o build.
    """
    caminho = Path(raiz) / 'consultas/gatilhos.json'
    if not caminho.exists():
        return []
    dados = json.loads(caminho.read_text(encoding='utf-8'))
    if dados.get('formato') != FORMATO or not isinstance(dados.get('gatilhos'), dict):
        raise ValueError(f'gatilhos.json: formato esperado {FORMATO}')
    por_id = {d['chave']: d for d in dispositivos}
    avisos, proprios = [], {}
    for chave, g in dados['gatilhos'].items():
        d = por_id.get(chave)
        if d is None:
            raise ValueError(f'Gatilho com ID inexistente: {chave}')
        if not d['elegivel']:
            raise ValueError(f'Gatilho em dispositivo inelegível (revogado/editorial): {chave}')
        condicoes = g.get('condicoes') if isinstance(g, dict) else None
        if not isinstance(condicoes, list) or not condicoes:
            raise ValueError(f'{chave}: condicoes vazias')
        for c in condicoes:
            _condicao(chave, c, d['norma'], por_id)
        if g.get('texto_sha256') != _sha(d['texto']):
            # Curadoria feita sobre outra redação: não aplicar até nova conferência.
            avisos.append(f'{chave}: redação mudou; gatilho ignorado até nova curadoria')
            continue
        fontes = []
        atual = d
        while atual is not None:
            fontes.append(atual)
            atual = por_id.get(atual.get('pai'))
        saida = []
        for c in condicoes:
            alvo = [por_id[c['em']]] if c.get('em') else fontes
            if not any(_normal(c['trecho']) in _normal(x['texto']) for x in alvo):
                raise ValueError(f'{chave}: trecho não encontrado: {c["trecho"]!r}')
            saida.append({**{k: v for k, v in c.items() if k != 'em'}, 'origem': chave})
        proprios[chave] = saida
    for d in dispositivos:
        if not d['elegivel']:
            continue
        cadeia, atual = [], d
        while atual is not None:
            cadeia.append(atual['chave'])
            atual = por_id.get(atual.get('pai'))
        herdados = [c for k in reversed(cadeia) for c in proprios.get(k, [])]
        if herdados:
            d['gatilhos'] = herdados
    return avisos


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gerar_grafo import RAIZ, gerar
    ds = {d['chave']: d for d in gerar(RAIZ, '0' * 40)[0]['dispositivos']}
    for chave in sys.argv[1:]:
        d = ds.get(chave)
        print(chave, _sha(d['texto']) if d else 'INEXISTENTE')
        if d:
            print('  ', texto_limpo(d['texto']))
