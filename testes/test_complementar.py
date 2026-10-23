import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from sincronizar_ctresb import parse

PATH='reguladores/conama/resolucoes/2025/teste.md'
HEADER='''---
titulo: "Resolução CONAMA 999"
tipo: "Resolução"
numero: "999"
data: 2025-01-01
revogada: null
fonte: "https://example.org"
---
'''
class ComplementarTest(unittest.TestCase):
    def test_literal_lines_and_whole_article(self):
        text=HEADER+'**Art. 1º** Exige licença.\n\n**§ 1º** Exceto o caso descrito.\n\n**Art. 2º** Vigência.\nANEXO I\nTabela\n'
        doc, reason=parse(text,PATH,'a'*40)
        self.assertIsNone(reason)
        self.assertEqual(doc['vigencia'],'nao_verificada')
        self.assertEqual(len(doc['artigos']),2)
        a=doc['artigos'][0]
        self.assertIn('Exceto',a['texto'])
        self.assertEqual(a['texto'],'\n'.join(text.splitlines()[a['linhas'][0]-1:a['linhas'][1]]).strip())
        self.assertNotIn('Tabela',doc['artigos'][-1]['texto'])
    def test_repealed(self):
        self.assertEqual(parse(HEADER.replace('revogada: null','revogada: true')+'**Art. 1º** Teste',PATH,'a'*40)[1],'revogada')
    def test_ambiguous_versions(self):
        self.assertEqual(parse(HEADER+'**Art. 1º** Original\n**Art. 1º** Atual',PATH,'a'*40)[1],'artigos_ambiguos')
    def test_struck_article(self):
        self.assertEqual(parse(HEADER+'**Art. 1º** ~~Texto antigo~~',PATH,'a'*40)[1],'sem_artigos_seguros')
