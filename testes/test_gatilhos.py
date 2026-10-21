import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import gatilhos
from gerar_grafo import gerar, fatias


def disp(chave, texto, pai=None):
    return dict(chave=chave, norma=chave.split('#')[0], texto=texto, pai=pai, elegivel=True)


class GatilhosTest(unittest.TestCase):
    def aplicar(self, ds, entradas):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'consultas').mkdir()
            (root / 'consultas/gatilhos.json').write_text(json.dumps(
                {'formato': gatilhos.FORMATO, 'gatilhos': entradas}), encoding='utf-8')
            return gatilhos.aplicar(ds, root)

    def entrada(self, d, *condicoes):
        return {'texto_sha256': hashlib.sha256(d['texto'].encode()).hexdigest(), 'condicoes': list(condicoes)}

    def test_filho_herda_condicao_do_caput(self):
        cpt = disp('n#art1_cpt', '**Art. 1º, caput** {#art1_cpt} O lançamento em rede coletora deve observar:')
        inc = disp('n#art1_cpt_inc1', '- **inciso I** {#art1_cpt_inc1} pH entre 5 e 9;', 'n#art1_cpt')
        c = {'campo': 'efluentes', 'valores': ['lancamento rede coletora esgoto'], 'trecho': 'lançamento em rede coletora'}
        self.assertEqual(self.aplicar([cpt, inc], {cpt['chave']: self.entrada(cpt, c)}), [])
        self.assertEqual(inc['gatilhos'][0]['origem'], 'n#art1_cpt')
        self.assertEqual(inc['gatilhos'], cpt['gatilhos'])

    def test_trecho_precisa_existir_na_norma(self):
        d = disp('n#art1_cpt', 'Se houver radiologia, tratar reveladores.')
        with self.assertRaises(ValueError):
            self.aplicar([d], {d['chave']: self.entrada(d, {'fato': 'Possui instalação radiativa.', 'trecho': 'instalação radiativa'})})

    def test_estrutura_invalida_interrompe_build(self):
        d = disp('n#art1_cpt', 'Se houver radiologia, tratar reveladores.')
        casos = [
            {'campo': 'porte', 'valores': ['x'], 'trecho': 'houver radiologia'},
            {'campo': 'efluentes', 'valores': [], 'trecho': 'houver radiologia'},
            {'campo': 'efluentes', 'valores': ['x'], 'fato': 'Fato e campo juntos.', 'trecho': 'houver radiologia'},
            {'fato': 'Usa radiologia.', 'trecho': 'curto'},
            {'fato': 'Usa radiologia.', 'trecho': 'houver radiologia', 'em': 'outra#art2'},
        ]
        for c in casos:
            with self.subTest(c=c), self.assertRaises(ValueError):
                self.aplicar([d], {d['chave']: self.entrada(d, c)})
        with self.assertRaises(ValueError):
            self.aplicar([d], {'n#inexistente': self.entrada(d, {'fato': 'Usa radiologia.', 'trecho': 'houver radiologia'})})

    def test_redacao_alterada_desativa_gatilho(self):
        d = disp('n#art1_cpt', 'Se houver radiologia, tratar reveladores.')
        e = self.entrada(d, {'fato': 'Usa radiologia.', 'trecho': 'houver radiologia'})
        d['texto'] += ' Nova redação.'
        avisos = self.aplicar([d], {d['chave']: e})
        self.assertEqual(len(avisos), 1)
        self.assertNotIn('gatilhos', d)

    def test_acervo_sem_gatilho_desatualizado_e_fatias(self):
        root = Path(__file__).resolve().parents[1]
        ds, graph = gerar(root, 'a' * 40)
        por_id = {d['chave']: d for d in ds['dispositivos']}
        curados = json.loads((root / 'consultas/gatilhos.json').read_text(encoding='utf-8'))['gatilhos']
        for chave in curados:
            self.assertIn('gatilhos', por_id[chave], chave + ': redação mudou; refazer a curadoria')
        f = fatias(ds, graph)['rdc-anvisa-222-2018']
        art81 = next(d for d in f['dispositivos'] if d['id'] == 'art81_cpt')
        self.assertEqual(art81['gatilhos'][0]['campo'], 'efluentes')


if __name__ == '__main__':
    unittest.main()
