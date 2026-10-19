#!/usr/bin/env python3
"""Verifica a integridade dos artefatos de consulta híbrida (sem dependências)."""
import argparse
import json
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]


def validar(dispositivos, grafo, raiz=RAIZ):
    raiz = Path(raiz)
    erros = []
    if dispositivos.get("formato") != "dispositivos/1":
        erros.append("formato do índice de dispositivos incompatível")
    if grafo.get("formato") != "grafo/1":
        erros.append("formato do grafo incompatível")
    if dispositivos.get("commit") != grafo.get("commit"):
        erros.append("índices produzidos a partir de commits diferentes")
    documentos = dispositivos.get("documentos", {})
    itens = dispositivos.get("dispositivos", [])
    chaves = {d.get("chave") for d in itens}
    if len(chaves) != len(itens):
        erros.append("chaves de dispositivos duplicadas")
    arquivos = {}

    for d in itens:
        chave = d.get("chave", "")
        norma, sep, ident = chave.partition("#")
        if not sep or norma != d.get("norma") or ident != d.get("id"):
            erros.append(f"chave malformada: {chave}")
        doc = documentos.get(norma)
        if not doc or d.get("arquivo") != doc.get("arquivo"):
            erros.append(f"documento inválido: {chave}")
            continue
        arquivo = d["arquivo"]
        if arquivo not in arquivos:
            caminho = raiz / arquivo
            arquivos[arquivo] = caminho.read_text(encoding="utf-8").splitlines() if caminho.is_file() else []
        linhas = arquivos[arquivo]
        a, b = d.get("linha_inicio", 0), d.get("linha_fim", 0)
        if not (1 <= a <= b <= len(linhas)):
            erros.append(f"intervalo de linhas inválido: {chave}")
            continue
        fonte = "\n".join(linhas[a-1:b])
        if f"{{#{ident}}}" not in fonte:
            erros.append(f"âncora não localizada na fonte: {chave}")
        if d.get("texto", "").strip() != fonte.rstrip().strip():
            erros.append(f"texto divergente da fonte: {chave}")
        pai = d.get("pai")
        if pai and pai not in chaves:
            erros.append(f"pai inexistente: {chave} -> {pai}")
        if d.get("situacao") in ("revogado", "revogada") and d.get("elegivel"):
            erros.append(f"dispositivo revogado elegível: {chave}")
        for tag in d.get("tags_herdadas", []):
            if tag in {"revogado", "redacao-alterada", "incluido"}:
                erros.append(f"tag de controle herdada indevidamente: {chave} {tag}")

    seen = set()
    arestas = grafo.get("arestas", [])
    for e in arestas:
        origem, destino, tipo = e.get("origem", ""), e.get("destino", ""), e.get("tipo", "")
        identidade = (origem, destino, tipo, e.get("fonte"))
        if identidade in seen:
            erros.append(f"aresta duplicada: {identidade}")
        seen.add(identidade)
        if origem not in documentos and origem not in chaves:
            erros.append(f"origem ausente: {origem}")
        existe = destino in chaves if "#" in destino else destino in documentos
        if e.get("resolvido") is not existe:
            erros.append(f"resolução de destino incorreta: {origem} -> {destino}")
        if tipo == "pertence_a" and (origem not in chaves or destino not in chaves):
            erros.append(f"hierarquia inválida: {origem} -> {destino}")
    pendentes = [e for e in arestas if not e["resolvido"]]
    if grafo.get("pendentes") != pendentes:
        erros.append("lista de pendências difere das arestas não resolvidas")
    return erros


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("diretorio", nargs="?", default="_site")
    a = cli.parse_args()
    pasta = Path(a.diretorio)
    ds = json.loads((pasta / "dispositivos.json").read_text(encoding="utf-8"))
    gr = json.loads((pasta / "grafo.json").read_text(encoding="utf-8"))
    erros = validar(ds, gr)
    for erro in erros[:100]:
        print("ERRO:", erro)
    print(f"{len(ds['dispositivos'])} dispositivos, {len(gr['arestas'])} arestas, "
          f"{len(gr['pendentes'])} pendentes, {len(erros)} erros")
    raise SystemExit(bool(erros))


if __name__ == "__main__":
    main()
