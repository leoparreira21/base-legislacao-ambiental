#!/usr/bin/env python3
"""Mede recuperação de evidências de uma bateria curada; não avalia respostas de LLM."""
import hashlib
import json
from pathlib import Path
import sys
from consultar import RAIZ, carregar, buscar


def conteudo_normalizado(p):
    return p.read_text(encoding='utf-8').encode('utf-8')


def executar():
    docs, blocos = carregar()
    casos = json.loads((RAIZ/'consultas/casos-auditoria.json').read_text(encoding='utf-8'))
    linhas = []
    for c in casos:
        esperado = set(c['esperados'])
        def evidencias(resultados):
            return {b['norma']+'#'+i for b in resultados for i in b['ids']}
        inicial = buscar(blocos, c['consulta_inicial'], frase=True)
        expandida = [b for q in c['consultas'] for b in buscar(blocos, q)]
        base, obtido = evidencias(inicial), evidencias(expandida)
        linhas.append({'id': c['id'], 'esperados': len(esperado),
                       'inicial_recuperados': len(esperado & base),
                       'expandida_recuperados': len(esperado & obtido),
                       'blocos_inicial': len(inicial),
                       'blocos_expandida': len({(b['arquivo'],b['linha']) for b in expandida}),
                       'omitidos_inicial': sorted(esperado-base),
                       'omitidos_expandida': sorted(esperado-obtido)})
    hash_corpus = hashlib.sha256()
    for p in sorted((RAIZ/'normas').rglob('*.md')):
        hash_corpus.update(p.relative_to(RAIZ).as_posix().encode()+b'\0'+conteudo_normalizado(p)+b'\0')
    return {'metodo': 'Frase literal inicial versus união de consultas temáticas cumulativas; todos os resultados, sem top-k. Casos e consultas curados juntos; não é benchmark independente nem execução de LLM.',
            'corpus_sha256': hash_corpus.hexdigest(), 'documentos': len(docs),
            'normas': sum('norma_mae' not in d['metadados'] for d in docs.values()),
            'anexos': sum('tipo_anexo' in d['metadados'] for d in docs.values()),
            'comentarios': sum(d['metadados'].get('tipo_documento')=='comentario' for d in docs.values()),
            'referencias_pendentes_distintas': len({n for d in docs.values() for n in d['pendentes']}),
            'casos': linhas,
            'total_esperados': sum(c['esperados'] for c in linhas),
            'total_inicial': sum(c['inicial_recuperados'] for c in linhas),
            'total_expandida': sum(c['expandida_recuperados'] for c in linhas)}


if __name__ == '__main__':
    r = executar()
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(1 if any(c['omitidos_expandida'] for c in r['casos']) else 0)
