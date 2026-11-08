import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from integrar_revisao_tags import build, normalize, AUDIT

class IntegracaoTagsTest(unittest.TestCase):
    def test_normalizacao_preserva_remissoes_e_limites(self):
        a = '**Art. 1** {#art1_cpt} #efluente Limite de 10 mg/L; [[norma#art2|artigo 2]].'
        b = '**Art. 8** {#art8_cpt} #outorga Limite de 10 mg/L; [[norma#art2|artigo 2]].'
        self.assertEqual(normalize(a), normalize(b))
        self.assertNotEqual(normalize(a), normalize(b.replace('10 mg/L', '20 mg/L')))
        self.assertNotEqual(normalize(a), normalize(b.replace('norma#art2', 'norma#art3')))

    def fixture(self, root, expected):
        (root / 'normas').mkdir()
        (root / AUDIT).mkdir(parents=True)
        body = 'O empreendedor deverá informar a destinação final dos resíduos sólidos e manter os comprovantes disponíveis para fiscalização, conforme as condições expressas no licenciamento ambiental.'
        for name in ['a', 'b']:
            (root / 'normas' / (name + '.md')).write_text('---\nnorma: '+name+'\nsituacao: vigente\ntags: [residuo-solido]\n---\n# Norma\n\n**Art. 1** {#art1_cpt} #residuo-solido '+body+'\n')
        d = {'cobertura': ['normas/a.md'], 'decisoes': [{'arquivo':'normas/a.md','id':'art1_cpt','antes':[], 'depois':expected,'evidencia':body,'justificativa':'Objeto expresso.'}]}
        (root / AUDIT / 'semantica-a.json').write_text(json.dumps(d))

    def test_grafo_identifica_repeticao_sem_replicar_decisao(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root, ['residuo-solido'])
            original=(root/'normas/b.md').read_bytes()
            manifest, graph, repeated=build(root)
            self.assertEqual(manifest['erros'], [])
            self.assertEqual(manifest['documentos_com_cobertura_registrada'], 1)
            self.assertEqual(len(repeated), 1)
            self.assertEqual(repeated[0]['ocorrencias_a_conferir'], ['normas/b.md#art1_cpt'])
            self.assertEqual((root/'normas/b.md').read_bytes(), original)
            self.assertTrue(all(e['relation']!='equivalente_juridico' for e in graph['edges']))

    def test_divergencia_documental_bloqueia_integracao(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root, ['efluente'])
            manifest, _, _=build(root)
            self.assertTrue(any('divergente' in e for e in manifest['erros']))
