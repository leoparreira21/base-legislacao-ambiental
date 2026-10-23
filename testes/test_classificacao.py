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

    def test_linha_de_tabela_herda_funcao_do_titulo(self):
        titulo = dict(chave='n#anexo2', id='anexo2', pai=None, elegivel=True, arquivo='normas/n.md',
                      tags_proprias=['las'], tags_herdadas=[],
                      texto='### ANEXO II {#anexo2}\n\nEnquadramento das atividades sujeitas a LAS. Deverá ser observado.')
        linha = dict(chave='n#anexo2_tab1_lin1', id='anexo2_tab1_lin1', pai='n#anexo2', elegivel=True,
                     arquivo='normas/n.md', tags_proprias=['las'], tags_herdadas=['las'],
                     texto='ATIVIDADE: Alimentos | Abatedouro de aves')
        with tempfile.TemporaryDirectory() as tmp:
            aplicar([titulo, linha], Path(tmp))
        self.assertEqual(linha['funcao']['categorias'], ['enquadramento'])  # obrigação não se herda
        self.assertIn('Herdada de anexo2', linha['funcao']['motivos']['enquadramento'][0])

    def test_heranca_por_tag_do_titulo_e_limites_exigem_numero(self):
        base = dict(pai=None, elegivel=True, arquivo='normas/n.md', tags_proprias=[],
                    tags_herdadas=['padrao-lancamento'])
        com_valor = dict(base, chave='n#art1_tab1_lin1', id='art1_tab1_lin1', texto='Parâmetro: Óleos | Padrão: 20')
        sem_valor = dict(base, chave='n#art1_tab1_lin2', id='art1_tab1_lin2', texto='Parâmetro: Óleos | Padrão: ausente')
        tag_da_linha = dict(base, chave='n#anexo1_lin1', id='anexo1_lin1', tags_proprias=['porte'],
                            tags_herdadas=[], texto='Descrever a área do terreno.')
        anexo_proprio = dict(base, chave='n-anexo3#anexo3_lin1', id='anexo3_lin1', tags_herdadas=['porte'],
                             arquivo='normas/anexos/n-anexo3.md', texto='Descrever a área do terreno.')
        with tempfile.TemporaryDirectory() as tmp:
            aplicar([com_valor, sem_valor, tag_da_linha, anexo_proprio], Path(tmp))
        self.assertEqual(com_valor['funcao']['categorias'], ['limites-parametros'])
        for d in (sem_valor, tag_da_linha, anexo_proprio):
            self.assertEqual(d['funcao']['categorias'], ['normas-gerais'], d['chave'])

    def test_acervo_e_fatias_com_ids_exatos(self):
        root = Path(__file__).resolve().parents[1]
        ds, graph = gerar(root, 'a'*40)
        by_id = {d['chave']: d for d in ds['dispositivos']}
        self.assertIn('limites-parametros', by_id['resolucao-conama-430-2011#art16_cpt_inc1_alia']['funcao']['categorias'])
        self.assertIn('licenciamento', by_id['resolucao-conama-237-1997#art8_cpt_inc1']['funcao']['categorias'])
        # Tabelas de anexo: enquadramento (LAS) e validade da LO herdam do título.
        self.assertIn('enquadramento', by_id['instrucao-normativa-iat-65-2025#anexo2_tab1_lin106']['funcao']['categorias'])
        self.assertIn('licenciamento', by_id['instrucao-normativa-iat-65-2025#anexo12_tab1_lin3']['funcao']['categorias'])
        for d in ds['dispositivos']:
            if d['elegivel']:
                self.assertTrue(set(d['funcao']['categorias']) <= set(CATEGORIAS))
            else:
                self.assertNotIn('funcao', d)
        f = fatias(ds, graph)['resolucao-conama-430-2011']
        self.assertTrue(all(d.get('funcao') for d in f['dispositivos']))


if __name__ == '__main__': unittest.main()
