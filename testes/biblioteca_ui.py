"""Regressão da biblioteca com HTML real e API simulada, sem acessar D1 ou IA.

python scripts/montar_biblioteca.py _biblioteca
python testes/biblioteca_ui.py
Requer o pacote Python playwright e Chromium (CHROMIUM_EXECUTABLE opcional).
"""
import os
import re
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

RAIZ = Path(__file__).resolve().parent.parent
SLUG = 'instrucao-normativa-iat-28-2026'
IDS = ['art19_cpt_inc6_alii', 'art34_cpt_inc6_alii', 'art42_cpt_inc9_alii', 'art46_cpt_inc9_alii']
TEXTO = 'sistema de tratamento de efluentes líquidos;'


def dispositivo(slug, id_html, rotulo, texto=TEXTO):
    return dict(legislacao_slug=slug, legislacao_nome=slug, legislacao_ementa='Súmula da API.',
                dispositivo_id_html=id_html, dispositivo_rotulo=rotulo, dispositivo_texto=texto,
                dispositivo_tipo='alinea', dispositivo_revogado=0, dispositivo_estrutura='Seção II')


ITENS = [dispositivo(SLUG, id_html, f'Art. {art}, caput, inciso {inciso}, alínea "i"')
         for id_html, art, inciso in zip(IDS, [19, 34, 42, 46], ['VI', 'VI', 'IX', 'IX'])]
CF = dispositivo('constituicao-federal-1988', 'art156-a_par6_inc6', 'Art. 156-A, § 6º, inciso VI', 'serviços de transporte coletivo')


class Servidor(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class BibliotecaUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = ThreadingHTTPServer(('127.0.0.1', 0), partial(Servidor, directory=str(RAIZ / '_biblioteca')))
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.servidor.server_port}'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE', '/usr/bin/chromium'), args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 1000})
        self.page.set_default_timeout(8000)
        self.erros = []
        self.page.on('pageerror', lambda e: self.erros.append(str(e)))
        self.falhar_lista = False
        self.itens = ITENS
        self.reter = False
        self.atrasadas = []
        self.pedidos = []
        self.page.route('**/api', lambda r: r.fulfill(json={'endpoints': {'buscar': 'Busca'}}))
        self.page.route('**/api/**', self.api)

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.erros, [])

    def api(self, route):
        if urlparse(route.request.url).path == '/api/filtros':
            route.fulfill(json={'tipos': [{'valor': 'IN IAT', 'total': 66}, {'valor': 'Lei', 'total': 363}],
                                'esferas': [{'valor': 'estadual', 'total': 160}, {'valor': 'federal', 'total': 692}],
                                'anos': [{'valor': 2026, 'total': 35}, {'valor': 2025, 'total': 60}]})
            return
        p = parse_qs(urlparse(route.request.url).query)
        self.pedidos.append(p)
        q = p.get('q', [''])[0]
        itens = [CF] if q == 'transporte' else self.itens if q == 'efluentes' else []
        if self.reter and 'tipo' not in p and 'slug' not in p:
            self.atrasadas.append(route)
            return
        if p.get('tipo') == ['caput']:
            itens = []
        if q == 'falha':
            route.fulfill(status=500, json={'erro': 'Falha de teste.'})
        elif 'slug' in p:
            if self.falhar_lista:
                route.fulfill(status=503, json={'erro': 'Consulta temporariamente indisponível.'})
            else:
                # Duas páginas para conferir que lista e localizador usam todos os
                # resultados, inclusive além do primeiro lote retornado pela API.
                offset = int(p.get('offset', ['0'])[0])
                route.fulfill(json={'resultados': itens[offset:offset + 2], 'proximo_offset': offset + 2 if len(itens) > offset + 2 else None})
        else:
            route.fulfill(json={'normas': [{**itens[0], 'ocorrencias': len(itens)}] if itens else []})

    def buscar(self, q='efluentes', mobile=False):
        if mobile:
            self.page.set_viewport_size({'width': 390, 'height': 844})
        self.page.goto(self.url, wait_until='networkidle')
        if mobile:
            self.page.get_by_role('button', name='Consulta no texto dos dispositivos').click()
        self.painel = self.page.get_by_role('complementary', name='Consulta no texto')
        self.painel.get_by_role('textbox').fill(q)
        self.painel.get_by_role('button', name='Buscar', exact=True).click()

    def abrir(self):
        self.painel.locator('li > button').first.click()
        self.localizador = self.page.get_by_role('region', name='Localizar ocorrências')
        expect(self.localizador.get_by_role('status')).to_have_text('1 de 4')
        self.frame = self.page.frame_locator('iframe')
        expect(self.frame.locator('.ocorrencia-consulta')).to_have_count(4)

    def test_sumula_lista_e_rotulos(self):
        self.buscar()
        cartao = self.painel.locator('li').first
        sumula = self.page.evaluate('(slug) => window.CATALOGO_NORMAS.find(n => n.arquivo === slug).ementa', SLUG)
        expect(cartao).to_contain_text(sumula)
        expect(cartao).not_to_contain_text(TEXTO)
        expect(cartao).not_to_contain_text('Art. 19')
        cartao.get_by_role('button', name='Ver os 4 dispositivos').click()
        expect(cartao).to_contain_text(TEXTO)
        rotulo = cartao.locator('ul button').first
        expect(rotulo).to_contain_text('Art. 19, VI, i')
        expect(rotulo.locator('i')).to_have_text('i')
        expect(cartao.locator('ul')).not_to_contain_text('caput')
        expect(cartao.locator('ul')).not_to_contain_text('inciso')
        expect(cartao.locator('ul')).not_to_contain_text('alínea')

    def test_paragrafo_e_ocorrencia_unica(self):
        self.buscar('transporte')
        self.painel.get_by_role('button', name='Ver o dispositivo', exact=True).click()
        expect(self.painel.locator('ul ul button')).to_contain_text('Art. 156-A, § 6º, VI')

    def test_exemplo_alinea_em_italico(self):
        self.itens = [{**ITENS[0], 'dispositivo_rotulo': 'Art. 8º, caput, inciso VII, alínea "h"'}]
        self.buscar()
        self.painel.get_by_role('button', name='Ver o dispositivo', exact=True).click()
        rotulo = self.painel.locator('ul ul button .text-primary')
        expect(rotulo).to_have_text('Art. 8º, VII, h')
        expect(rotulo.locator('i')).to_have_text('h')

    def test_localizador_ordem_ciclo_teclado_e_reabertura(self):
        self.buscar()
        self.abrir()
        expect(self.frame.locator('#art19_cpt_inc1')).not_to_have_attribute('open', '')
        self.frame.locator('body').evaluate('(el) => el.dataset.teste = "mesmo-documento"')
        self.localizador.get_by_role('button', name='Próxima ocorrência', exact=True).click()
        expect(self.localizador.get_by_role('status')).to_have_text('2 de 4')
        expect(self.frame.locator('#' + IDS[1])).to_have_class(re.compile(r'\bocorrencia-consulta-atual\b'))
        self.localizador.get_by_role('button', name='Ocorrência anterior', exact=True).click()
        self.localizador.get_by_role('button', name='Ocorrência anterior', exact=True).click()
        expect(self.localizador.get_by_role('status')).to_have_text('4 de 4')
        self.frame.locator('body').press('F3')
        expect(self.localizador.get_by_role('status')).to_have_text('1 de 4')
        self.frame.locator('body').press('Shift+F3')
        expect(self.localizador.get_by_role('status')).to_have_text('4 de 4')
        expect(self.frame.locator('body')).to_have_attribute('data-teste', 'mesmo-documento')
        self.frame.locator('body').press('Escape')
        expect(self.localizador).to_have_count(0)
        expect(self.frame.locator('.ocorrencia-consulta')).to_have_count(0)
        botao = self.page.get_by_role('button', name='Localizar ocorrências', exact=True)
        expect(botao).to_be_focused()
        botao.click()
        expect(self.page.get_by_role('region', name='Localizar ocorrências').get_by_role('status')).to_have_text('4 de 4')

    def test_mobile_e_falha_recuperavel(self):
        self.buscar(mobile=True)
        self.falhar_lista = True
        self.painel.locator('li > button').first.click()
        localizador = self.page.get_by_role('region', name='Localizar ocorrências')
        expect(localizador.get_by_role('alert')).to_contain_text('temporariamente indisponível')
        self.falhar_lista = False
        localizador.get_by_role('button', name='Tentar novamente').click()
        expect(localizador.get_by_role('status')).to_have_text('1 de 4')
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth > innerWidth'))
        localizador.get_by_role('button', name='Próxima ocorrência', exact=True).click()
        expect(localizador.get_by_role('status')).to_have_text('2 de 4')

    def test_filtros_limpeza_vazio_e_erro(self):
        self.buscar()
        self.abrir()
        self.painel.get_by_role('combobox', name='Tipo de dispositivo').select_option('caput')
        expect(self.painel).to_contain_text('Nenhuma norma')
        expect(self.localizador).to_have_count(0)
        self.painel.get_by_role('button', name='Limpar consulta no texto').click()
        expect(self.painel.get_by_role('textbox')).to_have_value('')
        expect(self.painel.get_by_role('textbox')).to_be_focused()
        self.painel.get_by_role('textbox').fill('falha')
        self.painel.get_by_role('button', name='Buscar', exact=True).click()
        expect(self.painel).to_contain_text('Falha de teste.')

    def test_resposta_atrasada_nao_sobrepoe_filtro(self):
        self.reter = True
        self.buscar()
        self.page.wait_for_timeout(100)
        self.assertEqual(len(self.atrasadas), 1)
        self.painel.get_by_role('combobox', name='Tipo de dispositivo').select_option('caput')
        # Mesmo antes da primeira resposta, mudar o filtro cancela a busca pendente.
        expect(self.painel).to_contain_text('Nenhuma norma')
        self.atrasadas[0].fulfill(json={'normas': [{**ITENS[0], 'ocorrencias': 4}]})
        self.page.wait_for_timeout(100)
        expect(self.painel.locator('li')).to_have_count(0)

    def test_modo_avancado_e_filtros_de_norma(self):
        self.buscar()
        expect(self.painel.locator('li').first).to_be_visible()
        self.assertEqual(self.pedidos[-1]['modo'], ['simples'])
        self.assertEqual(self.pedidos[-1]['ocultar_revogados'], ['true'])
        self.painel.get_by_role('button', name='Avançada', exact=True).click()
        expect(self.painel.get_by_role('button', name='Avançada', exact=True)).to_have_attribute('aria-pressed', 'true')
        self.painel.get_by_role('combobox', name='Tipo de norma').select_option('IN IAT')
        self.painel.get_by_role('combobox', name='Esfera').select_option('estadual')
        self.painel.get_by_role('combobox', name='Ano').select_option('2026')
        expect(self.painel.get_by_role('combobox', name='Tipo de norma')).to_contain_text('IN IAT (66)')
        self.page.wait_for_timeout(300)
        ultimo = self.pedidos[-1]
        self.assertEqual((ultimo['modo'], ultimo['tipo_norma'], ultimo['esfera'], ultimo['ano']),
                         (['avancado'], ['IN IAT'], ['estadual'], ['2026']))
        # a lista da norma e o localizador usam os mesmos filtros
        self.painel.get_by_role('button', name='Ver os 4 dispositivos').click()
        expect(self.painel).to_contain_text(TEXTO)
        self.assertEqual(self.pedidos[-1]['tipo_norma'], ['IN IAT'])
        self.painel.get_by_role('button', name='Limpar filtros').click()
        expect(self.painel.get_by_role('combobox', name='Ano')).to_have_value('')


if __name__ == '__main__':
    unittest.main(verbosity=2)
