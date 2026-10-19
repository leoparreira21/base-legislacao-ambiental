import json
from pathlib import Path
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

from gerar_grafo import gerar, salvar
from validar_indices import validar as validar_indices
from validar_resposta import validar as validar_resposta


class GrafoTeste(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dispositivos, cls.grafo = gerar(RAIZ, "a" * 40)
        cls.itens = {d["chave"]: d for d in cls.dispositivos["dispositivos"]}

    def test_granularidade_e_hierarquia(self):
        chave = "resolucao-conama-430-2011#art1_par1u"
        dispositivo = self.itens[chave]
        self.assertEqual(dispositivo["pai"], "resolucao-conama-430-2011#art1")
        self.assertIn("lançamento indireto", dispositivo["texto"])
        self.assertIn("lancamento-indireto", dispositivo["tags_herdadas"])
        self.assertTrue(dispositivo["elegivel"])

    def test_integridade_do_acervo(self):
        self.assertEqual(validar_indices(self.dispositivos, self.grafo, RAIZ), [])

    def test_nao_fundamentar_com_revogada(self):
        itens_revogados = [d for d in self.itens.values() if d["norma"] == "rdc-anvisa-306-2004"]
        self.assertTrue(itens_revogados)
        self.assertTrue(all(not d["elegivel"] for d in itens_revogados))

    def test_pendentes_distintos_de_erros(self):
        self.assertEqual(
            self.grafo["pendentes"],
            [a for a in self.grafo["arestas"] if not a["resolvido"]],
        )
        self.assertTrue(all(a["origem"] for a in self.grafo["pendentes"]))

    def test_verificador_da_resposta(self):
        chave = "resolucao-conama-430-2011#art1_par1u"
        trecho = "O lançamento indireto de efluentes no corpo receptor"
        resposta = {
            "versao": "consulta-hibrida/1", "commit": "a" * 40,
            "itens": [{
                "chave": chave, "classificacao": "condicionada",
                "fundamentacao": "A modalidade de lançamento deve ser confirmada.",
                "evidencias": [{"chave": chave, "trecho": trecho}],
            }], "lacunas": [],
        }
        self.assertEqual(validar_resposta(resposta, self.dispositivos), [])
        resposta["itens"][0]["evidencias"][0]["trecho"] = "Trecho inventado de texto que não existe"
        self.assertTrue(validar_resposta(resposta, self.dispositivos))
        resposta["itens"][0]["evidencias"][0]["trecho"] = trecho
        resposta["commit"] = "b" * 40
        self.assertTrue(validar_resposta(resposta, self.dispositivos))

    def test_sintese_interpretativa_nao_e_norma(self):
        anexos = [d for d in self.itens.values() if "/anexos/" in d["arquivo"]]
        self.assertTrue(any(d["natureza"] == "interpretativo" for d in anexos))
        self.assertTrue(all(not d["elegivel"] for d in anexos if d["natureza"] == "interpretativo"))

    def test_fixture_link_pendente_e_paragrafo(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            (raiz / "normas").mkdir()
            (raiz / "normas" / "lei-exemplo-2026.md").write_text(
                "---\nnorma: Exemplo\nsituacao: vigente\n"
                "cita: [\"[[lei-ausente-2000]]\"]\n---\n"
                "###### Art. 1º {#art1}\n"
                "Tags: #efluente\n"
                "**Art. 1º, caput** {#art1_cpt} Aplica-se em alguns casos.\n"
                "**Art. 1º, parágrafo único** {#art1_par1u} "
                "Ressalva [[lei-ausente-2000#art3|art. 3º]].\n",
                encoding="utf-8"
            )
            ds, gr = gerar(raiz, "b" * 40)
            nos = {d["chave"]: d for d in ds["dispositivos"]}
            par = nos["lei-exemplo-2026#art1_par1u"]
            self.assertEqual(par["pai"], "lei-exemplo-2026#art1")
            self.assertIn("efluente", par["tags_herdadas"])
            self.assertTrue(any(
                e["destino"] == "lei-ausente-2000#art3" and not e["resolvido"]
                for e in gr["arestas"]
            ))
            self.assertEqual(validar_indices(ds, gr, raiz), [])

    def test_publicacao_gera_artefatos(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta)
            salvar(saida, RAIZ, "c" * 40)
            ds = json.loads((saida / "dispositivos.json").read_text(encoding="utf-8"))
            gr = json.loads((saida / "grafo.json").read_text(encoding="utf-8"))
            self.assertEqual(ds["commit"], gr["commit"])
            self.assertEqual(ds["commit"], "c" * 40)
            self.assertGreater(len(ds["dispositivos"]), 1000)


if __name__ == "__main__":
    unittest.main()
