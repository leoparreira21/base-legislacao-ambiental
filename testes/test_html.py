"""Testes do gerador das páginas HTML de consulta (scripts/gerar_html.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import gerar_html as g  # noqa: E402

MD = """---
norma: Lei Teste nº 1/2026
ementa: "Ementa de teste."
situacao: vigente
---

# Lei Teste nº 1/2026 {#lei-teste-1-2026}

> **Ementa:** Ementa de teste.

## CAPÍTULO I – GERAL

### Seção I – Primeira

###### Art. 1º {#art1}
Tags: #teste

**Art. 1º, caput** {#art1_cpt} #teste Texto do caput, ver [[outra-norma#art2|art. 2º]]:
- **Art. 1º, caput, inciso I** {#art1_cpt_inc1} primeiro;
  - **Art. 1º, caput, inciso I, alínea "a"** {#art1_cpt_inc1_alia} alínea a;

**Art. 1º, parágrafo único** {#art1_par1u} Parágrafo.

## Notas de transcrição {#notas-transcricao}

Nota livre.

**Fecho** {#fecho} Brasília, 2026.
"""


def arvore():
    fm, corpo = g.ler_frontmatter(MD)
    conv = g.Conversor({'outra-norma'}, 'lei-teste-1-2026', Path('.'), Path('.'))
    titulo, cab, raiz = g.montar(corpo, conv)
    g.marcar_pais(raiz)
    return fm, titulo, cab, raiz


class TestGerarHtml(unittest.TestCase):
    def test_hierarquia(self):
        _, titulo, cab, raiz = arvore()
        self.assertEqual(titulo, 'Lei Teste nº 1/2026 {#lei-teste-1-2026}'.split(' {')[0])
        self.assertIn('Ementa de teste', cab[0])
        cap, notas, fecho = raiz.filhos()
        self.assertEqual((cap.tipo, notas.tipo, fecho.id), ('sec', 'sec', 'fecho'))
        secao = cap.filhos()[0]
        art = secao.filhos()[0]
        self.assertEqual(art.id, 'art1')
        cpt, par = art.filhos()
        self.assertEqual((cpt.tipo, par.id), ('cpt', 'art1_par1u'))
        inc = cpt.filhos()[0]
        self.assertEqual(inc.filhos()[0].id, 'art1_cpt_inc1_alia')
        self.assertTrue(cap.tem_artigo())
        self.assertFalse(notas.tem_artigo())

    def test_render(self):
        _, _, _, raiz = arvore()
        h = g.render(raiz)
        self.assertIn('<details class="sec estrutura n2"', h)
        self.assertIn('<details class="sec extra n2" id="notas-transcricao"', h)
        self.assertIn('<div class="cpt" id="art1_cpt">', h)
        self.assertIn('<summary title="Art. 1º, caput, inciso I">I</summary>', h)
        self.assertIn('<summary title="Art. 1º, caput, inciso I, alínea &quot;a&quot;">a)</summary>', h)
        self.assertIn('<a href="outra-norma.html#art2">art. 2º</a>', h)
        self.assertNotIn('#teste', h)

    def test_ancestrais_nr(self):
        self.assertEqual(list(g.ancestrais('ite13-1-3-1')), ['ite13-1-3', 'ite13-1', 'ite13'])
        self.assertEqual(list(g.ancestrais('art5_par2_inc3')), ['art5_par2', 'art5'])


if __name__ == '__main__':
    unittest.main()
