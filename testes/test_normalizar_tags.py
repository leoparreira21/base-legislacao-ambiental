import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from normalizar_tags import classificar  # noqa: E402


class TestNormalizarTags(unittest.TestCase):
    def test_historico_consistente(self):
        h = json.loads((ROOT / 'consultas/historico-tags.json').read_text(encoding='utf-8'))
        self.assertFalse(set(h['mescladas']) & set(h['mescladas'].values()), 'cadeia de mescla não resolvida')

    def test_classifica(self):
        h = json.loads((ROOT / 'consultas/historico-tags.json').read_text(encoding='utf-8'))
        orig, dest = next(iter(h['mescladas'].items()))
        exc = h['excluidas'][0]
        res, proposta, _ = classificar([orig, exc, 'revogado'])
        acoes = {r['tag']: r['acao'] for r in res}
        self.assertEqual(acoes[orig], 'trocar')
        self.assertEqual(acoes[exc], 'descartar')
        self.assertEqual(acoes['revogado'], 'descartar')
        self.assertIn(dest, proposta)


if __name__ == '__main__':
    unittest.main()
