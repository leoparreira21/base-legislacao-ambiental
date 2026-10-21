#!/usr/bin/env python3
"""Extração determinística para o grafo de conhecimento (graphify).

Lê `_site/dispositivos.json` (gerado por `scripts/gerar_site.py`) e monta
`graphify-out/.graphify_extract.json` com quatro tipos de nó:

- norma: arquivo de `normas/` (anexos e comentários somam na norma-mãe);
- categoria: enquadramento funcional dos dispositivos (classificar_dispositivos.py);
- tag: tags próprias dos dispositivos, sem as de controle e as estruturais;
- contexto: grupo de tags que aparecem juntas nos mesmos dispositivos
  (comunidades de Louvain no grafo de coocorrência de tags).

Arestas com `EXTRACTED` vêm do texto (tags, relações do frontmatter);
`INFERRED` vêm de contagem (categoria sugerida por regex, contextos).
Não usa LLM e não cria relação que não esteja nos índices.
"""
from __future__ import annotations

import collections
import json
import math
from pathlib import Path
import sys

import networkx as nx

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "graphify-out"

CATEGORIAS = {
    "enquadramento": "Específicas para enquadramento",
    "licenciamento": "Específicas para licenciamento",
    "obrigacoes-proibicoes": "Obrigações e proibições",
    "limites-parametros": "Limites de parâmetros",
    "normas-gerais": "Normas gerais",
}
# Controle de redação e marcas estruturais: aparecem em toda norma e não dizem o assunto.
TAGS_FORA = {
    "revogado", "redacao-alterada", "incluido", "anexo-pendente",
    "definicao", "vigencia", "revogacao", "alteracao", "ambito-aplicacao",
    "aplicabilidade", "publicacao-dioe",
}
RELACOES = ("regulamenta", "altera", "revoga", "cita")
MIN_NORMAS_TAG = 2        # tag precisa aparecer em ao menos 2 normas
MIN_PAR = 3               # dispositivos com o par de tags
MIN_COSSENO = 0.12        # associação mínima entre duas tags
MIN_TAGS_CONTEXTO = 3
PARTICIPA_CONTEXTO = 0.25  # fração das tags do contexto que a norma usa
MIN_TAGS_NORMA_CONTEXTO = 3
# Nome dado à mão a cada contexto, pela tag mais conectada dele. Contexto novo
# (tag âncora fora da lista) fica com as três primeiras tags como nome.
NOMES_CONTEXTO = {
    "reciclagem": "Gestão de resíduos sólidos (ciclo e destinação)",
    "dominialidade": "Documentação fundiária e cadastros (CAR, CTF, outorga)",
    "terra-indigena": "Áreas sensíveis e restrições locacionais",
    "supressao-vegetacao": "Modalidades e etapas de licença (LP, LI, LO, LAS)",
    "recuperacao-ambiental": "Regime florestal rural (PRA, manejo, uso alternativo)",
    "padrao-emissao": "Monitoramento, impacto e medidas mitigadoras",
    "sistema-isolamento": "Aterros e infraestrutura de disposição",
    "esgotamento-sanitario": "Atividades industriais e fontes poluidoras",
    "mapa-situacao": "Requerimento e documentos do processo",
    "dbo": "Padrões de qualidade e de lançamento",
    "sancao": "Infrações, sanções e responsabilidade",
    "dejeto-animal": "Agropecuária, efluentes no solo e áreas contaminadas",
    "recurso-hidrico": "Gestão de recursos hídricos (SEGRH)",
    "uso-solo": "Empreendimentos imobiliários e saneamento",
    "conservacao-solo": "Aptidão do solo, irrigação e aquicultura",
    "licenciamento-bifasico": "Rito de licenciamento e insumos orgânicos",
    "aii": "Áreas de influência e mananciais",
    "grupo-b": "Resíduos químicos (Grupo B) e aterro classe I",
}
PARTICIPA_CATEGORIA = 0.10
RESOLUCAO = float(__import__('os').environ.get('RESOLUCAO', '1.4'))


def ids(lista):
    """Converte '["[[a]]", "[[b|x]]"]' (texto do frontmatter) em ['a', 'b']."""
    if not lista:
        return []
    try:
        valores = json.loads(lista)
    except json.JSONDecodeError:
        valores = [lista]
    saida = []
    for v in valores:
        v = v.strip().strip("[]").split("|", 1)[0].split("#", 1)[0].strip()
        if v:
            saida.append(v)
    return saida


def no(ident, rotulo, tipo, fonte, **extra):
    base = {"id": ident, "label": rotulo, "file_type": tipo, "source_file": fonte,
            "source_location": None, "source_url": None, "captured_at": None,
            "author": None, "contributor": None}
    base.update(extra)
    return base


def aresta(origem, destino, relacao, confianca, score, fonte, peso=1.0):
    return {"source": origem, "target": destino, "relation": relacao,
            "confidence": confianca, "confidence_score": round(score, 3),
            "source_file": fonte, "source_location": None, "weight": round(peso, 3)}


def main():
    indice = json.loads((RAIZ / "_site/dispositivos.json").read_text(encoding="utf-8"))
    docs = indice["documentos"]
    mae = {k: (v["norma_mae"] or k) for k, v in docs.items()}
    normas = {k: v for k, v in docs.items() if v["natureza"] == "norma"}
    for k in list(mae):
        if mae[k] not in normas:  # comentário ou anexo órfão: liga pelo prefixo
            pref = next((n for n in normas if k.startswith(n)), None)
            mae[k] = pref
    disp = [d for d in indice["dispositivos"] if d["elegivel"] and mae.get(d["norma"])]

    # Contagens por norma.
    cat_norma = collections.defaultdict(collections.Counter)
    revisada = collections.defaultdict(int)
    tag_norma = collections.defaultdict(collections.Counter)
    tag_cat = collections.defaultdict(collections.Counter)
    conjuntos = []
    for d in disp:
        n = mae[d["norma"]]
        for c in d["funcao"]["categorias"]:
            cat_norma[n][c] += 1
        if d["funcao"].get("estado") == "revisada":
            revisada[n] += 1
        tags = sorted(set(d["tags_proprias"]) - TAGS_FORA)
        for t in tags:
            tag_norma[t][n] += 1
            for c in d["funcao"]["categorias"]:
                tag_cat[t][c] += 1
        if len(tags) >= 2:
            conjuntos.append((n, tags))

    tags_ok = {t for t, c in tag_norma.items() if len(c) >= MIN_NORMAS_TAG}
    freq = collections.Counter()
    pares = collections.Counter()
    for _, tags in conjuntos:
        tags = [t for t in tags if t in tags_ok]
        freq.update(tags)
        for i, a in enumerate(tags):
            for b in tags[i + 1:]:
                pares[(a, b)] += 1

    # Contextos: comunidades no grafo de coocorrência (peso = cosseno).
    co = nx.Graph()
    for (a, b), c in pares.items():
        cos = c / math.sqrt(freq[a] * freq[b])
        if c >= MIN_PAR and cos >= MIN_COSSENO:
            co.add_edge(a, b, weight=cos)
    grupos = nx.community.louvain_communities(co, weight="weight", resolution=RESOLUCAO, seed=42)
    grupos = sorted((sorted(g, key=lambda t: -co.degree(t, weight="weight"))
                     for g in grupos if len(g) >= MIN_TAGS_CONTEXTO), key=len, reverse=True)

    nodes, edges, hyper = [], [], []
    fonte_idx = "_site/dispositivos.json"

    for c, rot in CATEGORIAS.items():
        nodes.append(no(f"categoria_{c}", f"Categoria: {rot}", "concept", fonte_idx,
                        tipo_no="categoria"))

    for n, meta in normas.items():
        total = sum(cat_norma[n].values()) or 1
        especificas = {c: v for c, v in cat_norma[n].items() if c != "normas-gerais"}
        dominante = max(especificas, key=especificas.get) if especificas else "normas-gerais"
        nodes.append(no(f"norma_{n}", meta["titulo"], "document", meta["arquivo"],
                        tipo_no="norma", situacao=meta["situacao_cadastrada"],
                        categoria_dominante=dominante,
                        perfil_funcional={c: round(v / total, 3) for c, v in cat_norma[n].items()}))
        for c, v in cat_norma[n].items():
            share = v / total
            if share >= PARTICIPA_CATEGORIA or c == dominante:
                revisto = revisada[n] / total
                edges.append(aresta(f"norma_{n}", f"categoria_{c}", "enquadrada_em",
                                    "EXTRACTED" if revisto > 0.5 else "INFERRED",
                                    0.6 + 0.3 * share, fonte_idx, 1 + 4 * share))
        for campo in RELACOES:
            for alvo in ids(meta["metadados_relacoes"].get(campo, "")):
                if alvo in normas and alvo != n:
                    edges.append(aresta(f"norma_{n}", f"norma_{alvo}", campo,
                                        "EXTRACTED", 1.0, meta["arquivo"], 2.0))

    for t in sorted(tags_ok):
        cats = tag_cat[t]
        esp = {c: v for c, v in cats.items() if c != "normas-gerais"}
        nodes.append(no(f"tag_{t}", f"#{t}", "concept", "tags.md", tipo_no="tag",
                        categoria_dominante=max(esp, key=esp.get) if esp else "normas-gerais",
                        normas=len(tag_norma[t])))
        for n, v in tag_norma[t].items():
            edges.append(aresta(f"norma_{n}", f"tag_{t}", "tem_tag", "EXTRACTED", 1.0,
                                normas[n]["arquivo"], 1 + math.log10(v)))

    contextos = []
    for i, grupo in enumerate(grupos, 1):
        cid = f"contexto_{i:02d}"
        rotulo = NOMES_CONTEXTO.get(grupo[0], " + ".join(grupo[:3]))
        cats = collections.Counter()
        for t in grupo:
            cats.update(tag_cat[t])
        esp = {c: v for c, v in cats.items() if c != "normas-gerais"}
        dom = max(esp, key=esp.get) if esp else "normas-gerais"
        participantes = []
        for n in normas:
            usadas = [t for t in grupo if tag_norma[t].get(n)]
            frac = len(usadas) / len(grupo)
            if len(usadas) >= min(MIN_TAGS_NORMA_CONTEXTO, len(grupo)) and frac >= PARTICIPA_CONTEXTO:
                participantes.append((n, frac, usadas))
        participantes.sort(key=lambda x: -x[1])
        nodes.append(no(cid, f"Contexto: {rotulo}", "concept", "tags.md", tipo_no="contexto",
                        tags=grupo, categoria_dominante=dom))
        for t in grupo:
            edges.append(aresta(f"tag_{t}", cid, "compoe", "INFERRED",
                                min(0.95, 0.6 + co.degree(t, weight="weight") / 10),
                                "tags.md", 1.0))
        for n, frac, _ in participantes:
            edges.append(aresta(f"norma_{n}", cid, "atua_em", "INFERRED",
                                0.6 + 0.35 * frac, normas[n]["arquivo"], 1 + 3 * frac))
        edges.append(aresta(cid, f"categoria_{dom}", "predomina_em", "INFERRED", 0.7,
                            fonte_idx, 1.0))
        if len(participantes) >= 3:
            hyper.append({"id": f"{cid}_normas", "label": f"Normas no contexto {rotulo}",
                          "nodes": [f"norma_{n}" for n, *_ in participantes],
                          "relation": "participate_in", "confidence": "INFERRED",
                          "confidence_score": 0.7, "source_file": "tags.md"})
        contextos.append({"id": cid, "nome": rotulo, "tags": grupo, "categoria_dominante": dom,
                          "categorias": dict(cats.most_common()),
                          "normas": [{"norma": n, "fracao": round(f, 2), "tags": u}
                                     for n, f, u in participantes]})

    SAIDA.mkdir(exist_ok=True)
    (SAIDA / ".graphify_extract.json").write_text(json.dumps(
        {"nodes": nodes, "edges": edges, "hyperedges": hyper,
         "input_tokens": 0, "output_tokens": 0}, ensure_ascii=False, indent=1), encoding="utf-8")
    (SAIDA / "contextos.json").write_text(json.dumps(
        {"commit": indice["commit"], "parametros": {
            "min_normas_tag": MIN_NORMAS_TAG, "min_par": MIN_PAR, "min_cosseno": MIN_COSSENO,
            "participa_contexto": PARTICIPA_CONTEXTO, "tags_fora": sorted(TAGS_FORA)},
         "categorias_por_norma": {n: {"dominante": next(x["categoria_dominante"] for x in nodes if x["id"] == f"norma_{n}"),
                                      "perfil": dict(cat_norma[n].most_common())} for n in normas},
         "contextos": contextos}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(nodes)} nós ({len(normas)} normas, {len(tags_ok)} tags, {len(contextos)} contextos), "
          f"{len(edges)} arestas, {len(hyper)} hiperarestas; commit {indice['commit'][:7]}")


def relatorio():
    """Escreve graphify-out/AGRUPAMENTOS.md (rodar depois do build do graphify)."""
    ctx = json.loads((SAIDA / "contextos.json").read_text(encoding="utf-8"))
    grafo = json.loads((SAIDA / "graph.json").read_text(encoding="utf-8"))
    titulo = {n["id"][6:]: n["label"] for n in grafo["nodes"] if n["id"].startswith("norma_")}
    comunidade = {n["id"][6:]: n.get("community_name") or n.get("community")
                  for n in grafo["nodes"] if n["id"].startswith("norma_")}
    pct = lambda perfil, c: round(100 * perfil.get(c, 0) / (sum(perfil.values()) or 1))
    linhas = [
        "# Agrupamentos das normas", "",
        f"Gerado por `python scripts/grafo_conhecimento.py --relatorio` (commit {ctx['commit'][:7]}). "
        "Categorias vêm da pré-classificação funcional dos dispositivos (regex, estado *sugerida* "
        "salvo revisão humana); contextos são grupos de tags que aparecem juntas nos mesmos "
        "dispositivos. Nada aqui decide aplicabilidade.", "",
        "## 1. Por categoria funcional", "",
        "Categoria dominante = a categoria específica (fora \"normas gerais\") com mais dispositivos. "
        "Percentuais somam mais de 100% porque um dispositivo pode ter várias categorias.", "",
    ]
    por_cat = collections.defaultdict(list)
    for n, info in ctx["categorias_por_norma"].items():
        por_cat[info["dominante"]].append(n)
    cabec = "| Norma | " + " | ".join(CATEGORIAS) + " | Comunidade no grafo |"
    for c, rot in CATEGORIAS.items():
        if not por_cat[c]:
            continue
        linhas += [f"### {rot} ({len(por_cat[c])})", "", cabec,
                   "|" + "---|" * (len(CATEGORIAS) + 2)]
        for n in sorted(por_cat[c], key=lambda n: -pct(ctx["categorias_por_norma"][n]["perfil"], c)):
            perfil = ctx["categorias_por_norma"][n]["perfil"]
            linhas.append(f"| [[{n}\\|{titulo[n]}]] | " +
                          " | ".join(f"{pct(perfil, k)}%" for k in CATEGORIAS) +
                          f" | {comunidade[n]} |")
        linhas.append("")
    linhas += ["## 2. Por contexto (mistura de tags)", "",
               "Cada contexto junta tags que coocorrem nos dispositivos. Uma norma entra no contexto "
               f"quando usa ao menos {MIN_TAGS_NORMA_CONTEXTO} tags dele e {int(PARTICIPA_CONTEXTO * 100)}% "
               "do conjunto.", ""]
    for c in ctx["contextos"]:
        linhas += [f"### {c['nome']}", "",
                   f"- Categoria predominante: {CATEGORIAS[c['categoria_dominante']]}",
                   "- Tags: " + ", ".join(f"`#{t}`" for t in c["tags"]),
                   "- Normas: " + ("; ".join(f"[[{x['norma']}\\|{titulo[x['norma']]}]] ({int(x['fracao'] * 100)}%)"
                                             for x in c["normas"]) or "nenhuma acima do limiar"), ""]
    linhas += ["## 3. Contextos × categorias", "",
               "| Contexto | Predominante | Normas |", "|---|---|---|"]
    for c in ctx["contextos"]:
        linhas.append(f"| {c['nome']} | {CATEGORIAS[c['categoria_dominante']]} | {len(c['normas'])} |")
    (SAIDA / "AGRUPAMENTOS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("AGRUPAMENTOS.md escrito")


if __name__ == "__main__":
    sys.exit(relatorio() if "--relatorio" in sys.argv else main())
