#!/usr/bin/env python3
"""Validação determinística das citações geradas por um futuro agente de IA.

Não verifica aplicabilidade jurídica; rejeita IDs inventados, trechos inexistentes,
normas revogadas como fundamento positivo e commits divergentes.
Uso: python scripts/validar_resposta.py resposta.json _site/dispositivos.json
"""
import json
from pathlib import Path
import sys


CLASSIFICACOES = {"aplicavel", "condicionada", "contextual", "nao_aplicavel"}
POSITIVAS = {"aplicavel", "condicionada"}


def texto_plano(texto):
    # Para manter a comparação rigorosa, tolerar só quebras e espaços diferentes.
    return " ".join(str(texto).split())


def validar(resposta, indice):
    erros = []
    if resposta.get("versao") != "consulta-hibrida/1":
        erros.append("versão do contrato inválida")
    if resposta.get("commit") != indice.get("commit") or not indice.get("commit"):
        erros.append("commit da resposta não corresponde ao índice")
    dispositivos = {d["chave"]: d for d in indice.get("dispositivos", [])}
    itens = resposta.get("itens", [])
    if not isinstance(itens, list):
        return ["itens deve ser uma lista"]
    vistos = set()
    for pos, item in enumerate(itens):
        if not isinstance(item, dict):
            erros.append(f"item {pos}: estrutura inválida")
            continue
        chave = item.get("chave")
        classe = item.get("classificacao")
        if chave in vistos:
            erros.append(f"item duplicado: {chave}")
        vistos.add(chave)
        if classe not in CLASSIFICACOES:
            erros.append(f"classe inválida: {chave}")
        principal = dispositivos.get(chave)
        if principal is None:
            erros.append(f"dispositivo inventado: {chave}")
        elif classe in POSITIVAS and not principal.get("elegivel"):
            erros.append(f"fundamento não elegível: {chave}")
        if not str(item.get("fundamentacao", "")).strip():
            erros.append(f"fundamentação vazia: {chave}")
        evidencias = item.get("evidencias", [])
        if not isinstance(evidencias, list) or not evidencias:
            erros.append(f"item sem evidência: {chave}")
            continue
        if chave not in [e.get("chave") for e in evidencias if isinstance(e, dict)]:
            erros.append(f"item sem evidência principal: {chave}")
        for e in evidencias:
            if not isinstance(e, dict):
                erros.append(f"evidência inválida: {chave}")
                continue
            ref = e.get("chave")
            d = dispositivos.get(ref)
            if d is None:
                erros.append(f"citação inexistente: {chave} -> {ref}")
                continue
            if classe in POSITIVAS and not d.get("elegivel"):
                erros.append(f"citação não elegível para exigência: {chave} -> {ref}")
            trecho = texto_plano(e.get("trecho", ""))
            if len(trecho) < 10 or trecho not in texto_plano(d["texto"]):
                erros.append(f"trecho não encontrado literalmente: {chave} -> {ref}")
    if not isinstance(resposta.get("lacunas"), list):
        erros.append("lacunas deve ser uma lista")
    return erros


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python scripts/validar_resposta.py resposta.json _site/dispositivos.json")
    resposta = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    indice = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    erros = validar(resposta, indice)
    for erro in erros:
        print("ERRO:", erro)
    print(f"{len(erros)} erro(s) de integridade. Validação semântica ainda depende de revisão.")
    raise SystemExit(bool(erros))


if __name__ == "__main__":
    main()
