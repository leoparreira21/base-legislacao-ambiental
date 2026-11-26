#!/usr/bin/env python3
"""Importa para a área de entrada as normas do ctresb-leis que a base cita e ainda não tem.

Uso: python scripts/importar_ctresb.py ../ctresb-leis [--csv entrada/ctresb/correspondencias.csv]
     [--saida entrada/ctresb/normas]

O texto do ctresb é mantido. O script só faz correções mecânicas:
  1. nome do arquivo no padrão da base;
  2. frontmatter da base (os campos do ctresb são mantidos; os que conflitam ganham o sufixo _fonte);
  3. ementa tirada do corpo quando o ctresb não a traz (atos de órgãos);
  4. título H1 e citação da ementa no padrão da base;
  5. wikilinks nas menções a normas federais com número e data ("Lei nº 9.984, de 17 de julho de 2000");
  6. relações recíprocas preenchidas a partir das normas da base;
  7. tags de controle (#revogado, #redacao-alterada, #incluido) nas anotações dos textos compilados,
     fora das alterações entre aspas;
  8. seção "Notas de transcrição" com a origem e as mudanças feitas.
Nada vai para normas/. O log de cada norma sai em <saida>/../relatorio-importacao.csv.
"""
import argparse, csv, json, os, re, subprocess, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
MES_NUM = {m: i + 1 for i, m in enumerate(MESES)} | {"marco": 3}
# Nomes de arquivo corrigidos para o padrão do README (o link da base é que está fora do padrão).
RENOMEAR = {"decreto-lei-25-1937": "decreto-lei-federal-25-1937",
            "decreto-lei-3365-1941": "decreto-lei-federal-3365-1941",
            "decreto-lei-9760-1946": "decreto-lei-federal-9760-1946",
            "lei-federal-227-1967": "decreto-lei-federal-227-1967",
            "constituicao-estadual-pr": "constituicao-estadual-1989",
            "constituicao-estadual-pr-1989": "constituicao-estadual-1989"}
# Normas que Leo vai incluir ele mesmo (potabilidade e Normas Regulamentadoras): não entram por aqui.
EXCLUIR = {"portaria-ms-888-2021", "portaria-mtp-1846-2022", "portaria-mtp-806-2022", "portaria-mte-342-2024"}
TIPOS = [  # prefixo do arquivo -> (tipo, rótulo da norma)
    ("emenda-constitucional-revisao-federal-", "emenda-constitucional-revisao", "Emenda Constitucional de Revisão"),
    ("emenda-constitucional-federal-", "emenda-constitucional", "Emenda Constitucional"),
    ("lei-complementar-federal-", "lei-complementar", "Lei Complementar Federal"),
    ("decreto-legislativo-federal-", "decreto-legislativo", "Decreto Legislativo"),
    ("decreto-lei-federal-", "decreto-lei", "Decreto-Lei"),
    ("decreto-federal-", "decreto", "Decreto Federal"),
    ("lei-federal-", "lei", "Lei Federal"),
    ("medida-provisoria-", "medida-provisoria", "Medida Provisória"),
    ("rdc-anvisa-", "rdc", "RDC Anvisa"),
    ("portaria-mtp-", "portaria", "Portaria MTP"),
    ("portaria-mte-", "portaria", "Portaria MTE"),
    ("portaria-ms-", "portaria", "Portaria GM/MS"),
    ("portaria-ibama-", "portaria", "Portaria Ibama"),
    ("resolucao-conama-", "resolucao", "Resolução CONAMA"),
    ("resolucao-bcb-", "resolucao", "Resolução BCB"),
]
# Menção a norma federal com número e data, no texto corrido.
ESPECIE = {"Decreto-Lei": "decreto-lei-federal", "Lei Complementar": "lei-complementar-federal",
           "Lei": "lei-federal", "Decreto": "decreto-federal", "Medida Provisória": "medida-provisoria",
           "Emenda Constitucional": "emenda-constitucional-federal"}
MENCAO = re.compile(
    r"(?<![\w\-\[|])(Decreto-Lei|Lei Complementar|Lei|Decreto|Medida Provisória|Emenda Constitucional)"
    r"( Federal)? (?:n\.?\s?[º°]|nº|n°)\s?(\d{1,3}(?:\.\d{3})+|\d+)(-\d+)?,? de "
    r"(?:(\d{1,2})[º°]? de ([a-zç]+) de |(\d{1,2})\.(\d{1,2})\.)?(\d{4})")
# Anotação de compilado no fim de um dispositivo (fora de aspas).
ANOT = [("revogado", re.compile(r"\((?:\*)?Revogad[oa]s?\b|\(Revogad[oa]s?\)")),
        ("redacao-alterada", re.compile(r"\(Reda[çc][ãa]o dada")),
        ("incluido", re.compile(r"\((?:Inclu[íi]d[oa]|Acrescid[oa]|Acrescentad[oa])"))]


def num_fmt(n):
    base, _, reed = n.partition("-")
    s = f"{int(base):,}".replace(",", ".") if base.isdigit() else base
    return s + ("-" + reed if reed else "")


def ler_fm(texto):
    cab, corpo = texto[4:].split("\n---\n", 1)
    campos = []
    for linha in cab.splitlines():
        m = re.match(r"^([A-Za-z_][\w]*): ?(.*)$", linha)
        if m:
            campos.append([m.group(1), m.group(2)])
        elif campos:
            campos[-1][1] += "\n" + linha
    return campos, corpo


def valor(v):
    v = v.strip()
    if v.startswith('"'):
        try:
            return json.loads(v)
        except ValueError:
            return v.strip('"')
    return v


def aspas(s):
    return json.dumps(s, ensure_ascii=False)


def relacoes_da_base():
    """Para cada alvo, as relações que as normas da base já declaram sobre ele."""
    inv = {"alterado_por": "altera", "regulamentado_por": "regulamenta", "revogado_por": "revoga",
           "altera": "alterado_por", "regulamenta": "regulamentado_por", "revoga": "revogado_por"}
    rel = {}
    for f in glob.glob(os.path.join(RAIZ, "normas", "*.md")):
        t = open(f, encoding="utf-8").read()
        if not t.startswith("---\n"):
            continue
        nome = os.path.basename(f)[:-3]
        cab = t[4:].split("\n---\n", 1)[0]
        for campo, oposto in inv.items():
            m = re.search(rf"^{campo}: ?(.*)$", cab, re.M)
            for alvo in re.findall(r"\[\[([a-z0-9-]+)", m.group(1) if m else ""):
                rel.setdefault(alvo, {}).setdefault(oposto, set()).add(nome)
    return rel


def ementa_do_corpo(corpo):
    for linha in corpo.splitlines()[:25]:
        s = linha.strip().strip("*").strip()
        if re.match(r"^(Dispõe|Estabelece|Regulamenta|Altera|Aprova|Institui|Define|Disciplina|Atualiza|Cria|"
                    r"Fixa|Prorroga|Revoga|Torna|Inclui|Acrescenta|Determina|Autoriza|Consolida|Promulga)\b", s):
            return s
    return ""


def linkar(corpo, proprio, estadual=False):
    """Em texto estadual, "Lei nº" sem "Federal" é lei do Estado; em texto federal, número de lei acima de 16.000 não existe."""
    citas, n = [], 0

    def troca(m):
        nonlocal n
        especie, numero, reed, ano = m.group(1), m.group(3).replace(".", ""), m.group(4) or "", m.group(9)
        prefixo = ESPECIE[especie]
        if estadual and not m.group(2):
            prefixo = prefixo.replace("-federal", "-estadual").replace("emenda-constitucional", "emenda-constitucional-estadual")
        elif especie == "Lei" and int(numero) > 16000:
            return m.group(0)
        alvo = f"{prefixo}-{int(numero)}{reed}-{ano}".replace("-estadual-estadual", "-estadual")
        if alvo == proprio:
            return m.group(0)
        n += 1
        if alvo not in citas:
            citas.append(alvo)
        return f"[[{alvo}|{m.group(0)}]]"

    saida = []
    for linha in corpo.split("\n"):
        if linha.lstrip().startswith(("<", "#")) or "[[" in linha:
            saida.append(linha)
        else:
            saida.append(MENCAO.sub(troca, linha))
    return "\n".join(saida), citas, n


def tags_controle(corpo):
    """Acrescenta a tag de controle às linhas anotadas do texto compilado, fora das citações entre aspas."""
    saida, dentro, cont = [], False, {}
    for linha in corpo.split("\n"):
        s = linha.strip()
        abre = bool(re.match(r'^(\*\*)?[“"]', s))
        if abre and not dentro and not re.search(r'[”"]\s*(\(NR\))?\.?$', s):
            dentro = True
        elif dentro and re.search(r'[”"]\s*(\(NR\))?[.;]?\s*$|\(NR\)', s):
            dentro = False
            saida.append(linha)
            continue
        if not dentro and not abre and s and not s.startswith(("#", "<", "|", ">")):
            novas = [t for t, rx in ANOT if rx.search(s) and f"#{t}" not in s]
            if novas:
                linha = linha.rstrip() + " " + " ".join("#" + t for t in novas)
                for t in novas:
                    cont[t] = cont.get(t, 0) + 1
        saida.append(linha)
    return "\n".join(saida), cont


ROMANOS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def romano(r):
    total, ant = 0, 0
    for ch in reversed(r):
        v = ROMANOS[ch]
        total, ant = (total - v, ant) if v < ant else (total + v, v)
    return total if total and gerar_romano(total) == r else None


def gerar_romano(n):
    s = ""
    for v, sim in [(100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= v:
            s, n = s + sim, n - v
    return s


B = r"\**\s*"  # negrito em qualquer ponto do rótulo
RX_ART = re.compile(rf"^{B}Art{B}\.?{B}(\d{{1,3}}(?:\.\d{{3}})+|\d+)\**([º°]|o(?=[\s*.]))?\**(?:-([A-Z]{{1,2}})\b)?{B}[.:]?{B}[-–]?\s*(.*)$")
RX_ART_UNICO = re.compile(rf"^{B}Artigo [úu]nico{B}[.:]?{B}[-–]?\s*(.*)$", re.I)
RX_PAR = re.compile(rf"^{B}§{B}(\d+)\**([º°]|o(?=[\s*.]))?\**(?:-([A-Z])\b)?{B}[.:]?{B}[-–]?\s*(.*)$")
RX_PAR_UNICO = re.compile(rf"^{B}Par[áa]grafo [úu]nico{B}[.:]?{B}[-–]?\s*(.*)$", re.I)
RX_INC = re.compile(rf"^{B}([IVXLC]+)(?:-([A-Z]))?{B}\s*[-–—]\s*(.*)$")
RX_ALI = re.compile(rf"^{B}([a-z])(?:-([A-Z]))?\){B}\s*(.*)$")
RX_ITE = re.compile(r"^(\d{1,2})[.)]\s+(.*)$")
RX_ANEXO = re.compile(r"^(?:#+\s*)?\**\s*ANEXO(?:\s+([IVXLC]+|[ÚU]NICO|\d+))?\s*\**\s*[.:]?\s*(?:[-–—]\s*(.*))?$")
RX_REGULAMENTO = re.compile(r"^(ANEXO|REGULAMENTO|CONSOLIDAÇÃO|CÓDIGO|ESTATUTO)\b")
RX_FECHO = re.compile(r"^\**\s*(Brasília|Rio de Janeiro|Curitiba|Petrópolis|Palácio)\b.{0,80}\d{4}")
RX_TAGS_FIM = re.compile(r"((?:\s+#(?:revogado|redacao-alterada|incluido))+)\s*$")


def ord_(n):
    return f"{n}º" if int(str(n).replace(".", "")) < 10 else str(n)


def gerar_ids(corpo):
    """IDs LexML e rótulos completos a partir dos rótulos do texto (Art., §, parágrafo único, incisos,
    alíneas, itens). Alterações entre aspas e linhas ambíguas ficam como estão."""
    saida, ids, cont = [], set(), {"artigos": 0, "dispositivos": 0, "repetidos": 0, "anexos": 0}
    art = par = inc = ali = None
    rot_art = rot_par = rot_inc = rot_ali = ""
    pref, rot_pref, pausa, dentro, fecho = "", "", False, False, False

    onde = {}  # id -> (posição em saida, linha original)

    def disp(ident, rotulo, texto, nivel):
        if ident in ids:
            cont["repetidos"] += 1
            # Redação nova logo depois da antiga (texto anotado, como o da SETI): o ID passa para a nova.
            if ident in onde and re.search(r"\((Reda[çc][ãa]o dada|Inclu[íi]d)", texto):
                pos, bruta = onde.pop(ident)
                saida[pos] = bruta
            else:
                return None
        ids.add(ident)
        onde[ident] = (len(saida), linha)
        cont["dispositivos"] += 1
        m = RX_TAGS_FIM.search(texto)
        tags = ""
        if m:
            tags, texto = m.group(1).strip() + " ", texto[:m.start()]
        return ("  " * (nivel - 1) + "- " if nivel else "") + f"**{rotulo}** {{#{ident}}} {tags}{texto.strip()}".rstrip()

    numerados = set()
    for l in corpo.split("\n"):
        mm = RX_ANEXO.match(l.strip()) if len(l) < 200 else None
        if mm and mm.group(1):
            nn = mm.group(1).upper()
            numerados.add(int(nn) if nn.isdigit() else (1 if nn.startswith(("Ú", "U")) else romano(nn)))
    for linha in corpo.split("\n"):
        s = linha.strip()
        if s.startswith("## Notas de transcrição"):
            pausa = True
        abre = bool(re.match(r'^(\*\*)?[“"]', s))
        if dentro:
            if re.search(r'[”"]\s*(\(NR\))?[.;]?\s*$|\(NR\)', s):
                dentro = False
            saida.append(linha)
            continue
        if abre and art and not pausa:
            if not re.search(r'[”"]\s*(\(NR\))?[.;]?\s*$|\(NR\)', s):
                dentro = True
            saida.append(linha)
            continue
        if linha.startswith("###### ") and not RX_ART.match(s[7:]):
            linha = "#####" + linha[6:]
        m = RX_ANEXO.match(s) if len(s) < 200 and not s.startswith("## Notas") else None
        limpo = s.replace("**", "").replace("&lt;&lt;", "").replace(">>", "").strip()
        if (fecho and not m and not pref and RX_REGULAMENTO.match(limpo) and limpo == limpo.upper()
                and "anexo1" not in ids):
            # decreto que aprova regulamento (ou consolidação) "anexo" sem título ANEXO: o texto depois do fecho
            ids.add("anexo1")
            cont["anexos"] += 1
            saida.append(f"### {limpo} {{#anexo1}}")
            pref, rot_pref, fecho = "anexo1_", "Anexo, ", False
            art = par = inc = ali = None
            continue
        if m and (art or fecho or pref) and not pausa:
            num = (m.group(1) or "").upper()
            if not num:
                # "ANEXO" sem número: anexo1, salvo se o texto também tiver "ANEXO 1"/"ANEXO I"
                ident, rot_a = ("anexo" if 1 in numerados else "anexo1"), "Anexo"
            elif num.startswith(("Ú", "U")):
                ident, rot_a = "anexo1", "Anexo Único"
            else:
                n = int(num) if num.isdigit() else romano(num)
                ident, rot_a = (f"anexo{n}", f"Anexo {num}") if n else (None, "")
            if ident and ident not in ids:
                ids.add(ident)
                cont["anexos"] += 1
                titulo = re.sub(r"^#+\s*", "", s).replace("**", "").strip()
                saida.append(f"### {titulo} {{#{ident}}}")
                pref, rot_pref = ident + "_", rot_a + ", "
                art = par = inc = ali = None
                fecho = False
                continue
        if re.match(r"^(?:#+\s*)?\**\s*ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS\s*\**$", s) and "adct" not in ids:
            ids.add("adct")  # na Constituição, o ADCT recomeça a numeração: IDs com prefixo adct_
            saida.append("## ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS {#adct}")
            pref, rot_pref, fecho = "adct_", "ADCT, ", False
            art = par = inc = ali = None
            continue
        if pausa or fecho or not s or s.startswith(("#", "<", "|", ">")):
            saida.append(linha)
            continue
        if art and pref in ("", "adct_") and RX_FECHO.match(s) and "fecho" not in ids:
            ids.add("fecho")
            saida.append(f"**Fecho** {{#fecho}} {s.replace('**', '').strip()}")
            fecho = True
            continue
        nova = None
        m = RX_ART.match(s) or RX_ART_UNICO.match(s)
        if m:
            if m.re is RX_ART_UNICO:
                aid, rot, texto = pref + "art1u", rot_pref + "Artigo único", m.group(1)
            else:
                n = m.group(1)
                letra = m.group(3)
                aid = pref + "art" + n.replace(".", "") + (f"-{letra.lower()}" if letra else "")
                rot = rot_pref + "Art. " + ord_(n) + (f"-{letra}" if letra else "")
                texto = m.group(4)
            if aid in ids:
                cont["repetidos"] += 1
                art = None   # numeração repetida: o artigo e seus dispositivos ficam sem ID
                saida.append(linha)
                continue
            ids.add(aid)
            cont["artigos"] += 1
            art, rot_art, par, inc, ali = aid, rot, aid + "_cpt", None, None
            rot_par = rot + ", caput"
            saida.append(f"###### {rot[len(rot_pref):]} (ADCT) {{#{aid}}}" if pref == "adct_" else f"###### {rot} {{#{aid}}}")
            saida.append("")
            nova = disp(art + "_cpt", rot_par, texto, 0)
        elif art:
            mp, mpu = RX_PAR.match(s), RX_PAR_UNICO.match(s)
            mi, ma, mt = RX_INC.match(s), RX_ALI.match(s), RX_ITE.match(s)
            if mp or mpu:
                if mpu:
                    par, rot_par, texto = art + "_par1u", rot_art + ", parágrafo único", mpu.group(1)
                else:
                    n, letra = int(mp.group(1)), mp.group(3)
                    par = art + f"_par{n}" + (f"-{letra.lower()}" if letra else "")
                    rot_par = rot_art + ", § " + ord_(n) + (f"-{letra}" if letra else "")
                    texto = mp.group(4)
                inc = ali = None
                nova = disp(par, rot_par, texto, 0)
            elif mi and romano(mi.group(1)):
                n, letra = romano(mi.group(1)), mi.group(2)
                inc = par + f"_inc{n}" + (f"-{letra.lower()}" if letra else "")
                rot_inc = rot_par + ", inciso " + mi.group(1) + (f"-{letra}" if letra else "")
                ali = None
                nova = disp(inc, rot_inc, mi.group(3), 1)
            elif ma:
                base_ = inc or par
                ali = base_ + f"_ali{ma.group(1)}" + (f"-{ma.group(2).lower()}" if ma.group(2) else "")
                rot_ali = (rot_inc if inc else rot_par) + f', alínea "{ma.group(1)}{"-" + ma.group(2) if ma.group(2) else ""}"'
                nova = disp(ali, rot_ali, ma.group(3), 2 if inc else 1)
            elif mt and (ali or inc):
                base_, rot_b, niv = (ali, rot_ali, 3 if inc else 2) if ali else (inc, rot_inc, 2)
                nova = disp(base_ + f"_ite{int(mt.group(1))}", rot_b + f", item {int(mt.group(1))}", mt.group(2), niv)
        saida.append(nova if nova is not None else linha)
    return "\n".join(saida), cont


TABELAS = os.path.join(RAIZ, "entrada", "ctresb", "tabelas")


def trocar_tabelas(nome, corpo):
    """Troca a N-ésima <table> do ctresb pelo bloco "<!-- tabela N -->" de entrada/ctresb/tabelas/<nome>.md,
    transcrito à mão no padrão da base (linhas de tabela com ID, ou texto, no caso das assinaturas)."""
    f = os.path.join(TABELAS, nome + ".md")
    if not os.path.exists(f):
        return corpo, 0, ""
    texto, _, notas = open(f, encoding="utf-8").read().partition("<!-- notas -->")
    partes = re.split(r"^<!-- tabela (\d+) -->[ \t]*$", texto, flags=re.M)
    blocos = {int(partes[i]): partes[i + 1].strip("\n") for i in range(1, len(partes), 2)}
    n = [-1]

    def troca(m):
        n[0] += 1
        return blocos.get(n[0], m.group(0))
    return re.sub(r"<table.*?</table>", troca, corpo, flags=re.S), len(blocos), notas.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ctresb")
    ap.add_argument("--csv", default=os.path.join(RAIZ, "entrada", "ctresb", "correspondencias.csv"))
    ap.add_argument("--saida", default=os.path.join(RAIZ, "entrada", "ctresb", "normas"))
    a = ap.parse_args()
    commit = subprocess.check_output(["git", "-C", a.ctresb, "rev-parse", "HEAD"], text=True).strip()
    os.makedirs(a.saida, exist_ok=True)
    base = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(RAIZ, "normas", "*.md"))}
    rel = relacoes_da_base()
    feitos, log = {}, []
    for lin in csv.DictReader(open(a.csv, encoding="utf-8-sig"), delimiter=";"):
        nome = RENOMEAR.get(lin["norma_na_base"], lin["norma_na_base"])
        if nome in feitos or nome in base or nome in EXCLUIR:
            continue
        caminho = lin["arquivo_ctresb"]
        campos, corpo = ler_fm(open(os.path.join(a.ctresb, caminho), encoding="utf-8").read())
        orig = {k: valor(v) for k, v in campos}
        mud = []
        if nome != lin["norma_na_base"]:
            mud.append(f"nome do arquivo {nome} (o link na base é {lin['norma_na_base']})")

        ano = re.search(r"-(\d{4})$", nome).group(1)
        numero = re.match(r".*?-(\d+(?:-\d+)?)-\d{4}$", nome)
        numero = numero.group(1) if numero else "s/n"
        if nome.startswith("constituicao-estadual"):
            tipo, rotulo, norma, h1 = "constituicao", "", "Constituição do Estado do Paraná de 1989", "Constituição do Estado do Paraná de 1989"
            esfera, uf = "estadual", "PR"
        else:
            pref, tipo, rotulo = next(t for t in TIPOS if nome.startswith(t[0]))
            esfera, uf = "federal", None
            norma = f"{rotulo} nº {num_fmt(numero)}/{ano}"
            data = str(orig.get("data") or "")
            if re.match(r"\d{4}-\d\d-\d\d", data):
                y, mth, d = data.split("-")
                h1 = f"{rotulo} nº {num_fmt(numero)}, de {int(d)}{'º' if d == '01' else ''} de {MESES[int(mth) - 1]} de {y}"
            else:
                h1 = norma

        ementa = orig.get("ementa") or ""
        if not ementa:
            ementa = ementa_do_corpo(corpo)
            mud.append("ementa tirada do corpo" if ementa else "sem ementa (não achada no corpo)")

        corpo, citas, n_links = linkar(corpo, nome, esfera == "estadual")
        if n_links:
            mud.append(f"{n_links} menções viraram wikilink ({len(citas)} normas)")
        cont = {}
        if lin["qualidade"].startswith("A"):
            corpo, cont = tags_controle(corpo)
            if cont:
                mud.append("tags de controle: " + ", ".join(f"#{k} ×{v}" for k, v in cont.items()))

        corpo, cids = gerar_ids(corpo)
        mud.append(f"IDs LexML: {cids['artigos']} artigos, {cids['dispositivos']} dispositivos"
                   + (f", {cids['anexos']} anexos" if cids['anexos'] else "")
                   + (f"; {cids['repetidos']} rótulos repetidos ficaram sem ID" if cids['repetidos'] else ""))

        corpo, ntab, notas_tab = trocar_tabelas(nome, corpo)
        if ntab:
            mud.append(f"{ntab} tabelas HTML transcritas no padrão da base (entrada/ctresb/tabelas/{nome}.md)")

        r = rel.get(nome, {})
        if r:
            mud.append("relações da base: " + "; ".join(f"{k} {len(v)}" for k, v in sorted(r.items())))
        rev_ctresb = str(orig.get("revogada")).lower() == "true"
        situacao = "revogada" if rev_ctresb or r.get("revogado_por") else "vigente"
        if situacao == "revogada":
            mud.append("situacao: revogada (" + ("ctresb" if rev_ctresb else "") +
                       (" e " if rev_ctresb and r.get("revogado_por") else "") +
                       ("revogado_por na base" if r.get("revogado_por") else "") + ")")

        def lst(xs):
            return "[" + ", ".join(aspas(f"[[{x}]]") for x in sorted(xs)) + "]"

        versao = orig.get("versao_texto", "")
        texto = "compilado (ctresb-leis: " + versao + ")" if "compilad" in versao else "original (ctresb-leis: " + versao + "); alterações posteriores não aplicadas"
        fm = [("norma", aspas(norma)), ("arquivo", nome), ("tipo", tipo), ("esfera", esfera)]
        if uf:
            fm.append(("uf", uf))
        fm += [("numero", aspas(numero) if "-" in numero or numero == "s/n" else numero), ("ano", ano)]
        if re.match(r"\d{4}-\d\d-\d\d", str(orig.get("data") or "")):
            fm.append(("data_assinatura", orig["data"]))
        for k in ("data_publicacao", "publicacao", "orgao"):
            if orig.get(k):
                fm.append((k, aspas(str(orig[k])) if k != "data_publicacao" else orig[k]))
        fm += [("ementa", aspas(ementa)), ("situacao", situacao), ("texto", aspas(texto)),
               ("regulamenta", lst(r.get("regulamenta", ()))), ("regulamentado_por", lst(r.get("regulamentado_por", ()))),
               ("altera", lst(r.get("altera", ()))), ("alterado_por", lst(r.get("alterado_por", ()))),
               ("revoga", lst(r.get("revoga", ()))), ("revogado_por", lst(r.get("revogado_por", ()))),
               ("cita", lst(citas)), ("tags", "[]"), ("fonte", aspas(str(orig.get("fonte", ""))))]
        usados = {k for k, _ in fm}
        fm.append(("origem", aspas(f"ctresb-leis {commit[:11]} {caminho}")))
        for k, v in campos:  # campos do ctresb, sem perder nenhum
            if k in ("data_publicacao", "publicacao", "orgao", "fonte"):
                continue
            if k in usados and str(valor(v)) == str(valor(dict(fm)[k])):
                continue  # mesmo valor já gravado no campo da base
            fm.append((k + "_fonte" if k in usados else k, v))

        # Título e ementa no padrão da base (o H1 do ctresb sai; a epígrafe do corpo fica).
        corpo = re.sub(r"\A\s*# .*\n", "", corpo, count=1)
        topo = f"\n# {h1} {{#{nome}}}\n\n> **Ementa:** {ementa}\n" if ementa else f"\n# {h1} {{#{nome}}}\n"
        mud.append("frontmatter e título no padrão da base")

        notas = ["", "## Notas de transcrição {#notas-transcricao}", "",
                 f"Fonte: repositório [ctresb-leis](https://github.com/leoparreira21/ctresb-leis), commit `{commit[:11]}`, "
                 f"arquivo `{caminho}`. Texto convertido pelo ctresb a partir de {orig.get('fonte', 'fonte não informada')}; "
                 f"versão do texto: {versao}. Importado por `scripts/importar_ctresb.py`, sem revisão contra a publicação oficial.", ""]
        if "compilad" not in versao:
            notas += ["**Texto original.** Esta é a redação publicada, sem as alterações posteriores. Se a norma foi alterada, "
                      "o texto não está atualizado.", ""]
        if lin["qualidade"].startswith("C"):
            notas += ["**Texto incompleto.** O ctresb só traz a retificação, a promulgação de partes vetadas ou um texto sem artigos; "
                      "o texto integral precisa vir da publicação oficial.", ""]
        if lin["qualidade"].startswith("R"):
            notas += ["**A revisar.** O ctresb traz uma republicação ou o corpo em HTML bruto do DOU.", ""]
        if notas_tab:
            notas += ["**Tabelas.** " + notas_tab, ""]
        notas += ["**IDs e rótulos** gerados pelo script a partir dos rótulos do texto. Os trechos de alteração de outras normas "
                  "entre aspas e os rótulos repetidos ficaram sem ID. Tags temáticas não se aplicam a estas normas.", "",
                  "Mudanças feitas na importação: " + "; ".join(mud) + ".", ""]
        corpo = corpo.rstrip() + "\n" + "\n".join(notas)

        saida = "---\n" + "\n".join(f"{k}: {v}" for k, v in fm) + "\n---\n" + topo + "\n" + corpo.lstrip("\n")
        open(os.path.join(a.saida, nome + ".md"), "w", encoding="utf-8").write(saida)
        feitos[nome] = 1
        log.append({"arquivo": nome, "origem": caminho, "qualidade": lin["qualidade"], "situacao": situacao,
                    "wikilinks": n_links, "normas_citadas": len(citas),
                    **{f"tag_{k}": cont.get(k, 0) for k in ("revogado", "redacao-alterada", "incluido")},
                    "relacoes_da_base": sum(len(v) for v in r.values()),
                    "artigos_com_id": cids["artigos"], "dispositivos_com_id": cids["dispositivos"],
                    "rotulos_repetidos_sem_id": cids["repetidos"], "mudancas": "; ".join(mud)})
    with open(os.path.join(os.path.dirname(a.saida), "relatorio-importacao.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(log[0]), delimiter=";")
        w.writeheader()
        w.writerows(log)
    print(f"{len(log)} normas gravadas em {a.saida}")


if __name__ == "__main__":
    main()
