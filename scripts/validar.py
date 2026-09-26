#!/usr/bin/env python3
"""Valida a base de legislação em Markdown.

Uso:
  python scripts/validar.py                 # valida todas as normas
  python scripts/validar.py --tags          # regrava tags.md com todas as tags em uso
  python scripts/validar.py --afetados NORMA
        # lista, em outras normas, os links que apontam para dispositivos
        # revogados ou alterados da NORMA (ex.: decreto-estadual-9541-2025)

Verificações (erro = código de saída 1):
  - frontmatter com os campos obrigatórios e 'situacao' válida
  - nome do arquivo igual ao campo 'arquivo'
  - IDs {#...} únicos no arquivo
  - rótulo "**Art. N..." coerente com o ID "artN..."
  - links internos [[#id]] e links entre normas [[norma#id]] apontando para IDs existentes
  - relações recíprocas: se A 'altera'/'revoga' B e B está na base, B precisa ter A em 'alterado_por'/'revogado_por'
Avisos (não bloqueiam):
  - normas citadas que ainda não estão na base (links pendentes)
"""
import re, sys, glob, os, collections

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "normas")
OBRIGATORIOS = ["norma", "arquivo", "tipo", "esfera", "numero", "ano", "ementa", "situacao",
                "regulamenta", "altera", "alterado_por", "revoga", "revogado_por", "cita", "tags", "fonte"]
SITUACOES = {"vigente", "revogada"}


def carregar():
    normas = {}
    for f in sorted(glob.glob(os.path.join(PASTA, "*.md"))):
        t = open(f, encoding="utf-8").read()
        if not t.startswith("---\n"):
            normas[os.path.basename(f)[:-3]] = {"fm": {}, "corpo": t, "erro_fm": True}
            continue
        fm_txt, corpo = t[4:].split("\n---\n", 1)
        fm = {}
        for linha in fm_txt.splitlines():
            m = re.match(r"^([a-z_]+): ?(.*)$", linha)
            if m:
                fm[m.group(1)] = m.group(2)
        normas[os.path.basename(f)[:-3]] = {"fm": fm, "corpo": corpo, "erro_fm": False}
    return normas


def lista(valor):
    return re.findall(r"\[\[([a-z0-9-]+)", valor or "")


def ids_de(corpo):
    return re.findall(r"\{#([\w-]+)\}", corpo)


def validar(normas):
    erros, avisos = [], []
    ids = {n: ids_de(d["corpo"]) for n, d in normas.items()}
    for n, d in normas.items():
        fm, corpo = d["fm"], d["corpo"]
        if d["erro_fm"]:
            erros.append(f"{n}: sem frontmatter"); continue
        for c in OBRIGATORIOS:
            if c not in fm:
                erros.append(f"{n}: campo '{c}' ausente no frontmatter")
        if fm.get("arquivo") and fm["arquivo"] != n:
            erros.append(f"{n}: campo 'arquivo' ({fm['arquivo']}) difere do nome do arquivo")
        if fm.get("situacao") and fm["situacao"] not in SITUACOES:
            erros.append(f"{n}: situacao '{fm['situacao']}' inválida (use {sorted(SITUACOES)})")
        dup = [i for i, c in collections.Counter(ids[n]).items() if c > 1]
        if dup:
            erros.append(f"{n}: IDs duplicados {dup}")
        for rot, i in re.findall(r"\*\*Art\. (\d+)(?:º|-[A-Z])?[^*]*\*\* \{#(art\d+)", corpo):
            if "art" + rot != re.match(r"art\d+", i).group(0):
                erros.append(f"{n}: rótulo 'Art. {rot}' com ID '{i}'")
        for i in sorted(set(re.findall(r"\[\[#([\w-]+)", corpo)) - set(ids[n])):
            erros.append(f"{n}: link interno quebrado [[#{i}]]")
        for alvo, ancora in re.findall(r"\[\[([a-z0-9-]+)#([\w-]+)", corpo):
            if alvo in normas and ancora not in ids[alvo]:
                erros.append(f"{n}: link [[{alvo}#{ancora}]] aponta para ID inexistente")
        pend = sorted(set(a for a in re.findall(r"\[\[([a-z0-9-]+)", fm.get("cita", "") + fm.get("regulamenta", "") + fm.get("revoga", "") + corpo) if a not in normas))
        if pend:
            avisos.append(f"{n}: {len(pend)} norma(s) citada(s) fora da base: {', '.join(pend)}")
        for campo, reciproco in [("altera", "alterado_por"), ("revoga", "revogado_por"), ("regulamenta", "regulamentado_por")]:
            for alvo in lista(fm.get(campo)):
                if alvo in normas and n not in lista(normas[alvo]["fm"].get(reciproco)):
                    erros.append(f"{n} '{campo}' {alvo}, mas {alvo} não tem {n} em '{reciproco}'")
        if fm.get("situacao") == "revogada" and not lista(fm.get("revogado_por")):
            avisos.append(f"{n}: situacao 'revogada' sem 'revogado_por'")
    return erros, avisos


def afetados(normas, alvo):
    corpo = normas[alvo]["corpo"]
    mudou = set()
    for linha in corpo.splitlines():
        if re.search(r"#revogado\b|#redacao-alterada\b", linha):
            mudou.update(re.findall(r"\{#([\w-]+)\}", linha))
    fm = normas[alvo]["fm"]
    autoras = set(lista(fm.get("alterado_por")) + lista(fm.get("revogado_por")))  # quem alterou já aponta de propósito
    achou = False
    for n, d in normas.items():
        if n == alvo or n in autoras:
            continue
        for ancora in re.findall(r"\[\[" + re.escape(alvo) + r"#([\w-]+)", d["corpo"]):
            if ancora in mudou or any(ancora.startswith(m + "_") for m in mudou):
                print(f"{n} -> [[{alvo}#{ancora}]] (dispositivo revogado ou alterado)")
                achou = True
    if not achou:
        print("Nenhuma outra norma aponta para dispositivos revogados/alterados de", alvo)


def gerar_tags(normas):
    uso = collections.Counter()
    for d in normas.values():
        limpo = re.sub(r"\{#[^}]+\}|\[\[[^\]]*\]\]|`[^`]*`", "", d["corpo"])
        uso.update(set(re.findall(r"(?<![\w/])#([a-z][a-z0-9-]*)", limpo)))
    linhas = ["# Tags da base", "", "Gerado por `python scripts/validar.py --tags`. Formato: minúsculas, sem acento, singular, hífen entre palavras.", "",
              "| Tag | Normas que usam |", "|---|---|"]
    linhas += [f"| `#{t}` | {c} |" for t, c in sorted(uso.items())]
    open(os.path.join(RAIZ, "tags.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print(f"tags.md gravado com {len(uso)} tags")


if __name__ == "__main__":
    normas = carregar()
    if "--tags" in sys.argv:
        gerar_tags(normas); sys.exit(0)
    if "--afetados" in sys.argv:
        afetados(normas, sys.argv[sys.argv.index("--afetados") + 1]); sys.exit(0)
    erros, avisos = validar(normas)
    for a in avisos:
        print("AVISO:", a)
    for e in erros:
        print("ERRO: ", e)
    print(f"\n{len(normas)} normas, {len(erros)} erro(s), {len(avisos)} aviso(s)")
    sys.exit(1 if erros else 0)
