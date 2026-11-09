#!/usr/bin/env python3
"""Valida a proposta taxonômica; não atesta a classificação jurídica dos textos."""
import json
import re
from pathlib import Path
from validar import carregar

ROOT = Path(__file__).resolve().parents[1]


def validar_taxonomia(data, usadas):
    erros = []
    nodes = {n['id']: n for n in data['nos']}
    if len(nodes) != len(data['nos']):
        erros.append('IDs duplicados')
    if set(nodes) != set(usadas):
        erros.append('Taxonomia diverge das tags usadas')
    for key, n in nodes.items():
        if n['grupo'] not in data['grupos']:
            erros.append(f'Grupo desconhecido: {key}')
        vistos = {key}
        parent = n.get('pai')
        while parent:
            if parent in vistos:
                erros.append(f'Ciclo: {key}')
                break
            if parent not in nodes:
                erros.append(f'Pai ausente: {key}')
                break
            vistos.add(parent)
            parent = nodes[parent].get('pai')
    for alias, target in data['aliases'].items():
        if target not in nodes or alias in nodes or alias in usadas:
            erros.append(f'Alias inválido: {alias}')
    return erros


if __name__ == '__main__':
    usadas = set()
    for d in carregar().values():
        limpo = re.sub(r'\{#[^}]+\}|\[\[[^\]]*\]\]|`[^`]*`', '', d['corpo'])
        usadas.update(re.findall(r'(?<![\w/])#([a-z][a-z0-9-]*)', limpo))
    data = json.loads((ROOT / 'consultas/taxonomia-tags.proposta.json').read_text())
    erros = validar_taxonomia(data, usadas)
    print('\n'.join(erros) if erros else f'{len(usadas)} tags, sem ciclos, aliases válidos, cobertura integral do vocabulário.')
    raise SystemExit(bool(erros))
