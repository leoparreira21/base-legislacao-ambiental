import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from consultar import RAIZ, carregar, buscar, texto_atual, normalizar
import validar
from auditar_consultas import executar, conteudo_normalizado


class ConsultaTest(unittest.TestCase):
    def test_resultado_arquivado(self):
        esperado = json.loads((RAIZ/'docs/auditoria/resultados-consultas.json').read_text(encoding='utf-8'))
        self.assertEqual(executar(), esperado)

    def test_normalizacao_lf_crlf(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, 'texto.md')
            p.write_bytes('água\nsolo\n'.encode('utf-8'))
            original = conteudo_normalizado(p)
            p.write_bytes('água\r\nsolo\r\n'.encode('utf-8'))
            self.assertEqual(original, conteudo_normalizado(p))
            p.write_bytes('água\r\nresíduo\r\n'.encode('utf-8'))
            self.assertNotEqual(original, conteudo_normalizado(p))

    @classmethod
    def setUpClass(cls):
        cls.docs, cls.blocos = carregar()

    def bloco(self, norma, id):
        return next(b for b in self.blocos if b['norma']==norma and id in b['ids'])

    def test_casos_recuperam_dispositivos(self):
        for c in executar()['casos']:
            with self.subTest(caso=c['id']):
                self.assertEqual(c['omitidos_expandida'], [])

    def test_revogada_nao_vira_fundamento_atual(self):
        self.assertFalse(any(b['norma']=='rdc-anvisa-306-2004' for b in self.blocos))
        _, bs = carregar(historico=True)
        self.assertTrue(any(b['norma']=='rdc-anvisa-306-2004' for b in bs))

    def test_revogacao_parcial_preserva_artigo_e_redacao_nova(self):
        b=self.bloco('decreto-estadual-9541-2025','art13_par4')
        self.assertNotIn('art13_cpt_inc4', b['ids'])
        self.assertNotIn('~~', b['texto'])
        self.assertIn('art13_cpt', b['ids'])
        self.assertIn('DLAM', b['texto'])

    def test_artigo_totalmente_revogado_nao_retorna_cabecalho(self):
        self.assertFalse(any('art34' in b['ids'] for b in self.blocos if b['norma']=='resolucao-conama-357-2005'))

    def test_nao_remove_redacao_atual_na_mesma_linha(self):
        self.assertIn('texto novo', texto_atual('**Art. 1º** {#art1_cpt} texto novo ~~texto velho~~'))
        self.assertNotIn('texto velho', texto_atual('**Art. 1º** {#art1_cpt} texto novo ~~texto velho~~'))

    def test_interpretacoes_separadas(self):
        self.assertTrue(all(b['natureza']=='texto-normativo' for b in self.blocos))
        self.assertFalse(any('Síntese do conversor' in b['texto'] for b in self.blocos))
        _, bs=carregar(interpretativo=True)
        self.assertTrue(any(b['natureza']=='interpretativo' and b['norma'].endswith('-coment') for b in bs))
        self.assertTrue(any(b['natureza']=='interpretativo' and 'Relação com normas superiores' in b['texto'] for b in bs))
        self.assertFalse(any('> Aplica-se' in b['texto'] for b in self.blocos if '/anexos/' in b['arquivo']))

    def test_unidades_preservadas(self):
        b=self.bloco('instrucao-normativa-iat-11-2026','anexo1_tab1_lin850')
        self.assertIn('30 litros/dia', b['texto'])
        b=self.bloco('portaria-iap-26-2006','anexo-in_tab1_lin1')
        self.assertIn('semana', b['texto'])

    def test_sanitaria_e_condicionantes_preservadas(self):
        self.assertIn('licença sanitária', self.bloco('rdc-anvisa-222-2018','art5_par1')['texto'])
        self.assertIn('se solicitado em licenciamentos anteriores', self.bloco('portaria-iap-26-2006','anexo-in_lin76')['texto'])

    def test_cnae_com_sem_pontuacao(self):
        self.assertEqual(buscar(self.blocos,'7500100'),buscar(self.blocos,'7500-1/00'))
        self.assertEqual(normalizar('ÁGUAS'), 'aguas')

    def test_grafo_inverso_encontra_norma_transversal(self):
        self.assertIn('instrucao-normativa-iat-29-2026',self.docs['resolucao-conama-430-2011']['relacoes_entrada'])

    def test_pendente_em_regulamentado_por(self):
        self.assertIn('decreto-federal-10936-2022', self.docs['lei-federal-12305-2010']['pendentes'])
        _, avisos=validar.validar(validar.carregar())
        self.assertTrue(any('decreto-federal-10936-2022' in a for a in avisos))

    def test_localizacao_exata_e_ids_existentes(self):
        for b in self.blocos:
            linhas=(RAIZ/b['arquivo']).read_text(encoding='utf-8').splitlines()
            fonte='\n'.join(linhas[b['linha']-1:b['linha_fim']])
            for id in b['ids']:
                self.assertIn('{#'+id+'}', fonte)

    def test_busca_vazia_e_ausente(self):
        self.assertEqual(buscar(self.blocos,''),[])
        self.assertEqual(buscar(self.blocos,'termo_inexistente_987654321'),[])

    def test_reciprocidade_inversa(self):
        ns=validar.carregar()
        ns['decreto-estadual-12799-2026']['fm']['altera']='[]'
        erros,_=validar.validar(ns)
        self.assertTrue(any("'alterado_por'" in e for e in erros))

    def test_frontmatter_incompleto_nao_derruba_validacao(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'quebrado.md').write_text('---\nnorma: teste\nsem fechamento', encoding='utf-8')
            with patch.object(validar,'PASTA',d):
                erros,_=validar.validar(validar.carregar())
                self.assertTrue(any('sem frontmatter' in e for e in erros))

    def test_fixture_paragrafo_conserva_caput_e_excecao(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'normas'); p.mkdir()
            (p/'n.md').write_text('---\nnorma: Teste\nsituacao: vigente\n---\n###### Art. 1 {#art1}\n**Art. 1, caput** {#art1_cpt} É vedado.\n**Art. 1, § 1** {#art1_par1} Exceto na hipótese específica.\n', encoding='utf-8')
            _,bs=carregar(Path(d))
            r=buscar(bs,'hipotese')
            self.assertEqual(len(r),1)
            self.assertIn('É vedado.',r[0]['texto'])
            self.assertIn('art1_cpt',r[0]['ids'])


if __name__=='__main__':
    unittest.main()
