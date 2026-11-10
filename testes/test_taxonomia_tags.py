import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from auditar_taxonomia_tags import validar_taxonomia

class TaxonomiaTest(unittest.TestCase):
    def setUp(self):
        self.data = {'grupos': ['tema'], 'aliases': {'antiga': 'filho'}, 'nos': [
            {'id': 'pai', 'grupo': 'tema', 'pai': None},
            {'id': 'filho', 'grupo': 'tema', 'pai': 'pai'}]}

    def test_arvore_valida(self):
        self.assertEqual(validar_taxonomia(self.data, {'pai', 'filho'}), [])

    def test_ciclo_e_pai_ausente(self):
        for parent in ['filho', 'ausente']:
            data = copy.deepcopy(self.data)
            data['nos'][0]['pai'] = parent
            self.assertTrue(validar_taxonomia(data, {'pai', 'filho'}))

    def test_vocabulario_e_alias_inconsistentes(self):
        self.assertTrue(validar_taxonomia(self.data, {'pai'}))
        self.data['aliases']['antiga'] = 'inexistente'
        self.assertTrue(validar_taxonomia(self.data, {'pai', 'filho'}))
