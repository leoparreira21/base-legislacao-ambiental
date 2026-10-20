import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from classificar_dispositivos import aplicar, classificar, CATEGORIAS
from gerar_grafo import gerar, fatias


class ClassificacaoTest(unittest.TestCase):
    def categorias(self, texto, contexto=''):
        return classificar(texto, contexto)['categorias']

    def test_funcoes_multiplas(self):
        c = self.categorias('A renovação da licença deverá ser requerida no prazo de 120 dias.')
        self.assertIn('licenciamento', c)
        self.assertIn('obrigacoes-proibicoes', c)
        self.assertNotIn('limites-parametros', c)

    def test_porte_nao_e_limite_ambiental(self):
        c = self.categorias('Porte pequeno: área construída até 2.000 m²; CNAE 3101-2/00.')
        self.assertIn('enquadramento', c)
        self.assertNotIn('limites-parametros', c)

    def test_parametros_efetivos(self):
        for texto in ['pH entre 5 a 9;', 'Arsênio total | VALOR MÁXIMO: 0,5 mg/L',
                      'DBO: remoção mínima de 60%.']:
            self.assertIn('limites-parametros', self.categorias(texto))

    def test_mencao_sem_valor_nao_fixa_limite(self):
        self.assertNotIn('limites-parametros', self.categorias('Deverá atender os padrões de emissão.'))
        self.assertNotIn('limites-parametros', self.categorias('Produto Comercial: Etanol | Concentração: 100% | CAS: 64-17-5'))

    def test_regras_nao_leem_tags_e_numeros_do_rotulo(self):
        c = self.categorias('**Art. 16, inciso II** {#art16_inc2} #licenca-previa #ph Definições gerais.')
        self.assertEqual(c, ['normas-gerais'])

    def test_contexto_nao_transfere_funcao_indiscriminadamente(self):
        self.assertEqual(self.categorias('Definição de empreendedor.', 'Licença prévia obrigatória.'), ['normas-gerais'])

    def test_revisao_vinculada_ao_texto(self):
        d = dict(chave='norma#art1_cpt', texto='É proibido lançar resíduos.', pai=None, elegivel=True)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'consultas').mkdir()
            target = root/'consultas/classificacao-revisada.json'
            r = {d['chave']: {'categorias': ['obrigacoes-proibicoes'],
                 'texto_sha256': hashlib.sha256(d['texto'].encode()).hexdigest()}}
            target.write_text(json.dumps(r), encoding='utf-8')
            aplicar([d], root); self.assertEqual(d['funcao']['estado'], 'revisada')
            d['texto'] += ' Outra redação.'
            aplicar([d], root); self.assertTrue(d['funcao']['revisao_desatualizada'])
            self.assertEqual(d['funcao']['estado'], 'sugerida')
            r[d['chave']]['categorias'] = ['inventada']
            target.write_text(json.dumps(r), encoding='utf-8')
            with self.assertRaises(ValueError): aplicar([d], root)

    def test_acervo_e_fatias_com_ids_exatos(self):
        root = Path(__file__).resolve().parents[1]
        ds, graph = gerar(root, 'a'*40)
        by_id = {d['chave']: d for d in ds['dispositivos']}
        self.assertIn('limites-parametros', by_id['resolucao-conama-430-2011#art16_cpt_inc1_alia']['funcao']['categorias'])
        self.assertIn('licenciamento', by_id['resolucao-conama-237-1997#art8_cpt_inc1']['funcao']['categorias'])
        for d in ds['dispositivos']:
            if d['elegivel']:
                self.assertTrue(set(d['funcao']['categorias']) <= set(CATEGORIAS))
            else:
                self.assertNotIn('funcao', d)
        f = fatias(ds, graph)['resolucao-conama-430-2011']
        self.assertTrue(all(d.get('funcao') for d in f['dispositivos']))


if __name__ == '__main__': unittest.main()
