#!/usr/bin/env python3
"""Índices adicionais para consulta híbrida: dispositivos íntegros e grafo explícito.

Não decide aplicabilidade, não infere efeitos jurídicos e não usa fontes externas.
Os índices são complementares ao index.json usado pelo motor do site.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from consultar import ler_documento, normalizar

RAIZ = Path(__file__).resolve().parents[1]
ANCORA = re.compile(r"\{#([\w-]+)\}")
WIKILINK = re.compile(r"\[\[([^\]\n]+)\]\]")
TAG = re.compile(r"(?<![\w/&])#([a-z][a-z0-9-]*)")
CABECALHO = re.compile(r"^(#{1,6})\s+")
CAMPOS_RELACAO = (
    "regulamenta", "regulamentado_por", "altera", "alterado_por",
    "revoga", "revogado_por", "cita", "comentarios", "anexos",
)
SECOES_EDITORIAIS = (
    "notas de transcricao", "historico de alteracoes",
    "sintese do conversor", "relacao com", "relacao entre",
    "notas do conversor",
)
TAGS_CONTROLE = {"revogado", "redacao-alterada", "incluido", "anexo-pendente"}


def extrair_tags(texto):
    # Wikilinks para #art1 não são tags.
    return sorted(set(TAG.findall(ANCORA.sub('', WIKILINK.sub('', texto)))))


def links(texto, norma):
    """Devolve referências explícitas sem inventar destinos de remissões vagas."""
    for match in WIKILINK.finditer(texto):
        corpo = match.group(1).split("|", 1)[0].strip().replace("\\|", "|")
        arquivo, sep, ancora = corpo.partition("#")
        arquivo = arquivo.strip() or norma
        if not re.fullmatch(r"[a-z0-9-]+", arquivo):
            continue
        if ancora and not re.fullmatch(r"[\w-]+", ancora):
            continue
        yield arquivo + ("#" + ancora if sep and ancora else "")


def ancestral(ident, ids):
    pedaco = ident
    while "_" in pedaco:
        pedaco = pedaco.rsplit("_", 1)[0]
        if pedaco in ids:
            return pedaco
    m = re.match(r"^(art\d+(?:-[a-z])?|anexo(?:-?[a-z]+|\d+))", ident)
    return m.group(1) if m and m.group(1) in ids and m.group(1) != ident else None


def natureza_secao(caminho, secoes):
    if "/comentarios/" in caminho:
        return "interpretativo"
    for titulo in secoes.values():
        if any(titulo.startswith(s) for s in SECOES_EDITORIAIS):
            return "interpretativo"
    if "/anexos/" in caminho and not any(t.startswith("texto do anexo") for t in secoes.values()):
        return "interpretativo"
    return "texto-normativo"


def extrair_documento(raiz, caminho):
    texto, fm, corpo = ler_documento(caminho)
    nome = caminho.stem
    arquivo = caminho.relative_to(raiz).as_posix()
    linhas = corpo.splitlines()
    inicio_corpo = len(texto.splitlines()) - len(linhas) + 1
    secoes = {}
    registros = []
    atual = None

    def fechar():
        nonlocal atual
        if atual is not None:
            atual["texto"] = "\n".join(atual.pop("_linhas")).rstrip()
            atual["tags_proprias"] = extrair_tags(atual["texto"])
            atual["situacao"] = ("revogada" if fm.get("situacao") == "revogada"
                                 else "revogado" if "revogado" in atual["tags_proprias"]
                                 else "vigencia_nao_certificada")
            atual["elegivel"] = (atual["natureza"] == "texto-normativo"
                                  and atual["situacao"] not in {"revogada", "revogado"})
            registros.append(atual)
            atual = None

    for numero, linha in enumerate(linhas, inicio_corpo):
        h = CABECALHO.match(linha)
        if h:
            nivel = len(h.group(1))
            secoes = {k: v for k, v in secoes.items() if k < nivel}
            secoes[nivel] = normalizar(ANCORA.sub("", linha[h.end():]))
        anchors = ANCORA.findall(linha)
        if anchors:
            fechar()
            for ident in anchors:
                reg = {
                    "chave": f"{nome}#{ident}", "norma": nome, "id": ident,
                    "arquivo": arquivo, "linha_inicio": numero, "linha_fim": numero,
                    "natureza": natureza_secao(arquivo, secoes), "_linhas": [linha],
                }
                if atual is None:
                    atual = reg
                else:
                    # Múltiplas âncoras na mesma linha: cada ID mantém fonte íntegra.
                    reg["texto"] = linha
                    reg["tags_proprias"] = extrair_tags(linha)
                    reg["situacao"] = "revogado" if "revogado" in reg["tags_proprias"] else "vigencia_nao_certificada"
                    reg["elegivel"] = reg["natureza"] == "texto-normativo" and reg["situacao"] != "revogado" and fm.get("situacao") != "revogada"
                    registros.append(reg)
        elif h:
            fechar()  # não misturar texto de outra seção no dispositivo anterior
        elif atual is not None:
            atual["_linhas"].append(linha)
            atual["linha_fim"] = numero
    fechar()
    return fm, arquivo, registros


def gerar(raiz=RAIZ, commit=""):
    raiz = Path(raiz)
    documentos, dispositivos = {}, []
    for caminho in sorted((raiz / "normas").rglob("*.md")):
        fm, arquivo, regs = extrair_documento(raiz, caminho)
        nome = caminho.stem
        documentos[nome] = {
            "arquivo": arquivo, "titulo": fm.get("norma", fm.get("documento", nome)).strip('"'),
            "situacao_cadastrada": fm.get("situacao", "ver norma_mae"),
            "natureza": "comentario" if fm.get("tipo_documento") else "anexo" if fm.get("tipo_anexo") else "norma",
            "norma_mae": next(links(fm.get("norma_mae", ""), nome), None),
            "metadados_relacoes": {campo: fm.get(campo, "") for campo in CAMPOS_RELACAO},
        }
        dispositivos.extend(regs)

    indice = {d["chave"]: d for d in dispositivos}
    ids_por_norma = {}
    for d in dispositivos:
        ids_por_norma.setdefault(d["norma"], set()).add(d["id"])

    for d in dispositivos:
        pai = ancestral(d["id"], ids_por_norma[d["norma"]])
        d["pai"] = f'{d["norma"]}#{pai}' if pai else None
        ancestrais = []
        a = d["pai"]
        vistos = set()
        while a and a not in vistos and a in indice:
            vistos.add(a)
            ancestrais.append(a)
            a = indice[a]["pai"] if "pai" in indice[a] else (
                f'{indice[a]["norma"]}#{ancestral(indice[a]["id"], ids_por_norma[indice[a]["norma"]])}'
                if ancestral(indice[a]["id"], ids_por_norma[indice[a]["norma"]]) else None
            )
        d["tags_herdadas"] = sorted(set().union(
            *(set(indice[p]["tags_proprias"]) - TAGS_CONTROLE for p in ancestrais)
        )) if ancestrais else []
        d["remissoes"] = sorted(set(links(d["texto"], d["norma"])))

    # Anexos: situação do acervo vem da norma-mãe quando não indicada no anexo.
    for d in dispositivos:
        doc = documentos[d["norma"]]
        mae = doc["norma_mae"]
        if (mae and doc["situacao_cadastrada"] == "ver norma_mae"
                and mae in documentos and documentos[mae]["situacao_cadastrada"] == "revogada"):
            d["situacao"] = "revogada"
            d["elegivel"] = False

    arestas = []
    vistos_arestas = set()

    def adicionar(origem, destino, tipo, fonte):
        existe = destino in indice if "#" in destino else destino in documentos
        chave = (origem, destino, tipo, fonte)
        if chave in vistos_arestas:
            return
        vistos_arestas.add(chave)
        arestas.append({
            "origem": origem, "destino": destino, "tipo": tipo,
            "fonte": fonte, "resolvido": existe,
        })

    for nome, doc in documentos.items():
        for campo, valor in doc["metadados_relacoes"].items():
            for destino in links(valor, nome):
                adicionar(nome, destino, campo, "frontmatter")
        if doc["norma_mae"]:
            adicionar(nome, doc["norma_mae"], "norma_mae", "frontmatter")

    for d in dispositivos:
        if d["pai"]:
            adicionar(d["chave"], d["pai"], "pertence_a", "hierarquia_id")
        for destino in d["remissoes"]:
            if destino != d["chave"]:
                adicionar(d["chave"], destino, "remete_para", "wikilink")

    arestas.sort(key=lambda e: (e["origem"], e["tipo"], e["destino"], e["fonte"]))
    dispositivos.sort(key=lambda d: (d["arquivo"], d["linha_inicio"], d["id"]))
    resultado = {
        "formato": "dispositivos/1", "commit": commit,
        "documentos": {k: documentos[k] for k in sorted(documentos)},
        "dispositivos": dispositivos,
    }
    grafo = {
        "formato": "grafo/1", "commit": commit, "arestas": arestas,
        "pendentes": [a for a in arestas if not a["resolvido"]],
    }
    return resultado, grafo


def salvar(destino, raiz=RAIZ, commit=""):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    dispositivos, grafo = gerar(raiz, commit)
    for arquivo, dados in (("dispositivos.json", dispositivos), ("grafo.json", grafo)):
        (destino / arquivo).write_text(
            json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    print(f"Índice híbrido: {len(dispositivos['dispositivos'])} dispositivos; "
          f"{len(grafo['arestas'])} relações; {len(grafo['pendentes'])} pendências.")
    return dispositivos, grafo


if __name__ == "__main__":
    salvar(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "_site")
