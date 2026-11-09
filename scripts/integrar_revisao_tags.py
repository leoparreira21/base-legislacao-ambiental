#!/usr/bin/env python3
"""Integra decisões auditáveis em um grafo no formato de extração do Graphify.

Não usa LLM, não aplica mudanças e não presume equivalência jurídica de textos
iguais. Lê os arquivos atuais; sha256 registra o conteúdo inclusive não commitado.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
from gerar_grafo import extrair_documento

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path('auditorias/tags-2026-11-07')
PROTECTED = re.compile(r'(\{#[^}]+\}|\[\[.*?\]\]|`[^`]*`)', re.S)
TAG = re.compile(r'(?<![\w/])#([a-z][a-z0-9-]*)')


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def tags(text):
    return sorted(set(TAG.findall(PROTECTED.sub('', text))))


def normalize(text):
    """Mantém remissões e números; ignora apenas marcação editorial de tags/IDs."""
    text = re.sub(r'^Tags:.*$', '', text, flags=re.M)
    text = ''.join(p if i % 2 else TAG.sub('', p)
                   for i, p in enumerate(PROTECTED.split(text)))
    text = re.sub(r'^\s*(?:[-*>]\s*)*\*\*[^*]+\*\*\s*(?=\{#)', '', text, flags=re.M)
    text = re.sub(r'\{#[^}]+\}', '', text)
    return ' '.join(text.split())


def build(root=ROOT):
    root = Path(root)
    audit = root / AUDIT
    docs, units, groups, hashes = {}, {}, collections.defaultdict(list), {}
    for path in sorted((root / 'normas').rglob('*.md')):
        fm, filename, regs = extrair_documento(root, path)
        docs[filename] = fm
        hashes[filename] = digest(path.read_text(encoding='utf-8'))
        for r in regs:
            key = filename + '#' + r['id']
            units[key] = r
            normalized = normalize(r['texto'])
            if (r['natureza'] == 'texto-normativo' and len(normalized) >= 100
                    and not re.match(r'^#{1,6}\s', r['texto'])):
                groups[digest(normalized)].append(key)
    decisions, covered, errors = {}, {}, []
    source_files = sorted(audit.glob('semantica-*.json'))
    for source in source_files:
        data = json.loads(source.read_text(encoding='utf-8'))
        src = source.relative_to(root).as_posix()
        hashes[src] = digest(source.read_text(encoding='utf-8'))
        cov = data.get('cobertura', [])
        if isinstance(cov, str):
            covered[data['arquivo']] = {'fonte': src, 'escopo': cov}
        else:
            for item in cov:
                f = item if isinstance(item, str) else item['arquivo']
                covered[f] = {'fonte': src, 'escopo': data.get('escopo', data.get('metodo', 'Conforme relatório do lote')), 'detalhe': item}
        for d in data.get('decisoes', []):
            f, ident = d['arquivo'], d['id']
            key = f + '#' + ident
            if f not in docs:
                errors.append(f'Documento ausente: {key}')
                continue
            if ident in {'frontmatter.tags', 'frontmatter', 'tags'}:
                actual = sorted(re.findall(r'[a-z][a-z0-9-]*', docs[f].get('tags', '')))
            elif key in units:
                actual = tags(units[key]['texto'])
            else:
                errors.append(f'ID ausente: {key}')
                continue
            expected = d.get('depois')
            if not isinstance(expected, list):
                errors.append(f'Decisão sem lista depois: {key}')
                continue
            if sorted(set(expected)) != sorted(set(actual)):
                errors.append(f'Decisão divergente do arquivo atual: {key}; esperado={expected}; atual={actual}')
            if key in decisions and decisions[key]['depois'] != expected:
                errors.append(f'Decisões conflitantes: {key}')
            decisions[key] = {**d, 'fonte_decisao': src}
    nodes, edges = {}, []

    def node(ident, label, file_type, source_file, **extra):
        nodes[ident] = {'id': ident, 'label': label, 'file_type': file_type,
                        'source_file': source_file, **extra}

    def edge(a, b, relation):
        edges.append({'source': a, 'target': b, 'relation': relation,
                      'confidence': 'EXTRACTED', 'confidence_score': 1.0})

    def unit_node(key):
        if key in nodes:
            return
        r = units[key]
        f = r['arquivo']
        file_id = 'arquivo:' + f
        node(file_id, f, 'document', f, sha256=hashes[f],
             cobertura=covered.get(f, {'escopo': 'Revisão integral não registrada'}))
        node(key, r['norma'] + '#' + r['id'], 'document', f,
             source_location=f"{r['linha_inicio']}:{r['linha_fim']}",
             texto=r['texto'], natureza=r['natureza'],
             situacao=r['situacao'], tags_diretas=tags(r['texto']))
        edge(key, file_id, 'pertence_ao_documento')

    for key, d in decisions.items():
        if key not in units:
            continue  # metadados são registrados no manifesto, não como dispositivo.
        unit_node(key)
        dec = 'decisao:' + digest(key)[:20]
        action = ('manter' if d.get('antes') == d['depois'] else
                  'acrescentar' if not d.get('antes') else
                  'remover' if not d['depois'] else 'substituir')
        node(dec, action + ': ' + key, 'document', d['fonte_decisao'],
             acao=action, antes=d.get('antes'), depois=d['depois'],
             justificativa=d.get('justificativa'), evidencia=d.get('evidencia'))
        edge(dec, key, 'revisa')
        for t in d['depois']:
            node('tag:' + t, '#' + t, 'concept', 'tags.md')
            edge(key, 'tag:' + t, 'tem_tag_direta')

    repeated = []
    for fingerprint, members in sorted(groups.items()):
        reviewed = [k for k in members if k in decisions]
        pending = [k for k in members if k not in decisions]
        if not reviewed or not pending or len({units[k]['arquivo'] for k in members}) < 2:
            continue
        ident = 'texto-identico:' + fingerprint
        sample = normalize(units[members[0]]['texto'])
        node(ident, 'Texto idêntico — conferir contexto antes de reaproveitar decisão',
             'concept', units[members[0]]['arquivo'], sha256=fingerprint)
        for member in members:
            unit_node(member)
            edge(member, ident, 'mesmo_texto_normalizado')
        repeated.append({'sha256': fingerprint, 'texto': sample,
                         'decisoes_existentes': reviewed, 'ocorrencias_a_conferir': pending,
                         'aviso': 'Identidade textual não prova aplicabilidade ou equivalência de tags; conferir norma-mãe, seção, remissões e vigência.'})

    manifest = {
        'formato': 'revisao-tags-integrada/1',
        'origem': 'arquivos locais atuais e relatórios explícitos; sem inferência por LLM',
        'graphify_conectado': {'estado': 'indisponivel', 'motivo': 'list_workspaces retornou [] em 2026-11-08; nada foi enviado à memória ou ao índice remoto'},
        'documentos_inventariados': len(docs), 'documentos_com_cobertura_registrada': len(covered),
        'cobertura': covered, 'decisoes': len(decisions),
        'decisoes_com_alteracao': sum(d.get('antes') != d['depois'] for d in decisions.values()),
        'grupos_textuais_para_reaproveitamento': len(repeated),
        'ocorrencias_a_conferir': sum(len(g['ocorrencias_a_conferir']) for g in repeated),
        'arquivos_sha256': hashes, 'erros': errors,
        'pendentes_de_revisao_integral': sorted(set(docs) - set(covered)),
        'limites': ['Cobertura declarada nos relatórios; o integrador não lê juridicamente o conteúdo.',
                    'O piloto CONAMA 430 anterior ao snapshot é registrado no relatório original e não incluído nestes totais.',
                    'Arestas de texto idêntico não são equivalência jurídica, hierarquia de tags ou prova de vigência.',
                    'Não replica automaticamente decisões em ocorrências sem revisão.']}
    return manifest, {'nodes': list(nodes.values()), 'edges': edges, 'hyperedges': []}, repeated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', help='Mostra só decisões/ocorrências com esta tag direta')
    parser.add_argument('--arquivo', help='Filtra por trecho do caminho do documento')
    parser.add_argument('--limite', type=int, default=20)
    args = parser.parse_args()
    manifest, graph, repeated = build()
    if args.tag or args.arquivo:
        found = [n for n in graph['nodes'] if 'tags_diretas' in n
                 and (not args.tag or args.tag in n['tags_diretas'])
                 and (not args.arquivo or args.arquivo in n['source_file'])]
        print(json.dumps({'total': len(found), 'resultados': found[:max(0, args.limite)]}, ensure_ascii=False, indent=2))
    else:
        for name, data in [('integracao-manifesto.json', manifest),
                           
                           ('integracao-repeticoes.json', repeated)]:
            (ROOT / AUDIT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        graph_dir = ROOT / 'graphify-out'
        graph_dir.mkdir(exist_ok=True)
        (graph_dir / 'revisao-tags.graphify.json').write_text(json.dumps(graph, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in manifest.items() if k not in {'cobertura', 'arquivos_sha256', 'pendentes_de_revisao_integral'}}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(manifest['erros']))


if __name__ == '__main__':
    main()
