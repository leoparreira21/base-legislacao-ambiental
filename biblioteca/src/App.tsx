import { useEffect, useMemo, useRef, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowLeft, ExternalLink, Search, X } from 'lucide-react'

type Norma = {
  arquivo: string
  norma: string
  tipo: string
  esfera: string
  orgao: string
  ano: number | null
  ementa: string
  situacao: string
  apelidos: string[]
}

declare global {
  interface Window { CATALOGO_NORMAS?: Norma[] }
}

// Pasta das páginas, relativa a esta página: html/ no site publicado e no artefato;
// ../html quando a biblioteca é aberta de site/ no repositório.
const PASTAS = ['html', '../html']
let PASTA = PASTAS[0]

const TIPOS: [string, string][] = [
  ['lei-complementar', 'Leis complementares'],
  ['lei', 'Leis'],
  ['decreto', 'Decretos'],
  ['resolucao', 'Resoluções'],
  ['rdc', 'RDCs (Anvisa)'],
  ['instrucao-normativa', 'Instruções normativas'],
  ['portaria', 'Portarias'],
  ['norma-regulamentadora', 'Normas regulamentadoras'],
  ['norma-cnen', 'Normas CNEN'],
]
const nomeTipo = (t: string) => TIPOS.find(([k]) => k === t)?.[1] ?? t
const ordemTipo = (t: string) => {
  const i = TIPOS.findIndex(([k]) => k === t)
  return i < 0 ? 99 : i
}

// sem acento, minúsculas, "6.938" = "6938"
const normalizar = (s: string) =>
  s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/(\d)\.(?=\d)/g, '$1')

function numero(n: Norma) {
  const m = n.arquivo.match(/-(\d+(?:-\d+)?)-\d{4}$/) || n.arquivo.match(/-(\d+(?:-\d+)?)$/)
  return m ? parseFloat(m[1].replace('-', '.')) : 0
}

function lerHash(): { arquivo: string; ancora: string } {
  const h = decodeURIComponent(location.hash.slice(1))
  const [arquivo = '', ancora = ''] = h.split('/')
  return { arquivo, ancora }
}

function carregarScript(pasta: string): Promise<Norma[]> {
  return new Promise((ok, falha) => {
    const s = document.createElement('script')
    s.src = `${pasta}/catalogo.js`
    s.onload = () => (window.CATALOGO_NORMAS ? ok(window.CATALOGO_NORMAS) : falha(new Error('catálogo vazio')))
    s.onerror = () => { s.remove(); falha(new Error('sem catálogo')) }
    document.head.appendChild(s)
  })
}

async function carregarCatalogo(): Promise<Norma[]> {
  for (const p of PASTAS) {
    try {
      const c = await carregarScript(p)
      PASTA = p
      return c
    } catch { /* tenta a próxima pasta */ }
  }
  throw new Error('não encontrei html/catalogo.js')
}

function Segmentado<T extends string>({ valor, opcoes, mudar, rotulo }: {
  valor: T; opcoes: [T, string][]; mudar: (v: T) => void; rotulo: string
}) {
  return (
    <div role="radiogroup" aria-label={rotulo} className="inline-flex rounded-md border bg-card p-0.5">
      {opcoes.map(([v, r]) => (
        <button
          key={v}
          role="radio"
          aria-checked={valor === v}
          onClick={() => mudar(v)}
          className={`rounded px-2.5 py-1 text-xs font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring ${
            valor === v ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          {r}
        </button>
      ))}
    </div>
  )
}

export default function App() {
  const [normas, setNormas] = useState<Norma[] | null>(null)
  const [erro, setErro] = useState('')
  const [q, setQ] = useState('')
  const [esfera, setEsfera] = useState<'todas' | 'federal' | 'estadual'>('todas')
  const [situacao, setSituacao] = useState<'todas' | 'vigente' | 'revogada'>('todas')
  const [tipos, setTipos] = useState<string[]>([])
  const [sel, setSel] = useState(lerHash)
  // endereço pedido ao leitor; muda só por escolha na lista ou no endereço da página,
  // não quando o leitor segue um link interno (senão recarregaria o documento)
  const [pedido, setPedido] = useState(lerHash)
  const [recarga, setRecarga] = useState(0)
  const busca = useRef<HTMLInputElement>(null)
  const quadro = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    carregarCatalogo().then(setNormas).catch((e) => setErro(e.message))
    const h = () => { setSel(lerHash()); setPedido(lerHash()); setRecarga((r) => r + 1) }
    window.addEventListener('hashchange', h)
    const tecla = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement?.tagName !== 'INPUT') {
        e.preventDefault()
        busca.current?.focus()
      }
    }
    window.addEventListener('keydown', tecla)
    return () => {
      window.removeEventListener('hashchange', h)
      window.removeEventListener('keydown', tecla)
    }
  }, [])

  const abrir = (arquivo: string, ancora = '') => {
    const novo = arquivo ? `#${arquivo}${ancora ? '/' + ancora : ''}` : ' '
    history.pushState(null, '', novo === ' ' ? location.pathname + location.search : novo)
    setSel({ arquivo, ancora })
    setPedido({ arquivo, ancora })
    setRecarga((r) => r + 1)
  }

  const presentesTipos = useMemo(() => {
    const c = new Map<string, number>()
    normas?.forEach((n) => c.set(n.tipo, (c.get(n.tipo) ?? 0) + 1))
    return [...c.entries()].sort((a, b) => ordemTipo(a[0]) - ordemTipo(b[0]))
  }, [normas])

  const filtradas = useMemo(() => {
    if (!normas) return []
    const termos = normalizar(q).split(/\s+/).filter(Boolean)
    return normas.filter((n) => {
      if (esfera !== 'todas' && n.esfera !== esfera) return false
      if (situacao !== 'todas' && n.situacao !== situacao) return false
      if (tipos.length && !tipos.includes(n.tipo)) return false
      if (!termos.length) return true
      const alvo = normalizar([n.norma, n.arquivo, n.ementa, n.orgao, ...n.apelidos].join(' '))
      return termos.every((t) => alvo.includes(t))
    })
  }, [normas, q, esfera, situacao, tipos])

  const grupos = useMemo(() => {
    const g = new Map<string, Norma[]>()
    filtradas.forEach((n) => g.set(n.tipo, [...(g.get(n.tipo) ?? []), n]))
    return [...g.entries()]
      .sort((a, b) => ordemTipo(a[0]) - ordemTipo(b[0]))
      .map(([t, ns]) => [t, ns.sort((a, b) => (b.ano ?? 0) - (a.ano ?? 0) || numero(b) - numero(a))] as const)
  }, [filtradas])

  const atual = normas?.find((n) => n.arquivo === sel.arquivo)
  const filtrosAtivos = q || esfera !== 'todas' || situacao !== 'todas' || tipos.length

  // O documento entra no leitor como srcdoc (texto baixado + <base>): funciona também onde a
  // página não pode embutir outros endereços (artefato). Sem fetch (aberto do disco, file://),
  // o leitor carrega o arquivo direto pelo src.
  const [doc, setDoc] = useState<{ n: number; html: string | null } | null>(null)
  useEffect(() => {
    if (!pedido.arquivo || !normas) return
    let vivo = true
    const n = recarga
    fetch(`${PASTA}/${pedido.arquivo}.html`)
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error(String(r.status)))))
      .then((t) => {
        const base = new URL(`${PASTA}/`, location.href).href
        if (vivo) setDoc({ n, html: t.replace(/<head>/i, `<head><base href="${base}">`) })
      })
      .catch(() => vivo && setDoc({ n, html: null }))
    return () => { vivo = false }
  }, [pedido.arquivo, recarga, normas])

  // mantém a norma aberta visível na lista (endereço direto, links entre normas)
  useEffect(() => {
    document.querySelector('nav a[aria-current="page"]')?.scrollIntoView({ block: 'nearest' })
  }, [sel.arquivo, normas])

  const ehNorma = (arq: string) => !!normas?.some((n) => n.arquivo === arq)

  // Liga o documento à biblioteca: esconde "Todas as normas" (a lista é esta), leva à âncora
  // pedida e abre na biblioteca os links para outras normas.
  const aoCarregar = () => {
    try {
      const win = quadro.current?.contentWindow
      const d = quadro.current?.contentDocument
      if (!win || !d) return
      d.querySelectorAll<HTMLAnchorElement>('.barra a[href$="index.html"]').forEach((a) => (a.style.display = 'none'))
      if (doc?.html) {
        if (pedido.ancora) win.location.hash = pedido.ancora
        d.addEventListener('click', (ev) => {
          const a = (ev.target as Element).closest?.('a[href]') as HTMLAnchorElement | null
          if (!a || ev.defaultPrevented) return
          const href = a.getAttribute('href') || ''
          if (href.startsWith('#')) {
            ev.preventDefault()
            win.location.hash = href.slice(1)
            return
          }
          const u = new URL(a.href)
          const arq = decodeURIComponent(u.pathname.split('/').pop() || '').replace(/\.html$/, '')
          if (u.origin === location.origin && u.pathname.endsWith('.html')) {
            ev.preventDefault()
            if (ehNorma(arq)) abrir(arq, decodeURIComponent(u.hash.slice(1)))
          } else {
            a.target = '_blank'
            a.rel = 'noopener'
          }
        })
      } else {
        const arq = decodeURIComponent(win.location.pathname.split('/').pop() || '').replace(/\.html$/, '')
        if (arq && arq !== sel.arquivo && ehNorma(arq)) {
          history.replaceState(null, '', `#${arq}`)
          setSel({ arquivo: arq, ancora: '' })
        }
      }
    } catch {
      /* origem diferente (ex.: file://): sem sincronização, o documento funciona igual */
    }
  }

  const pronto = doc && doc.n === recarga
  const src = pedido.arquivo ? `${PASTA}/${pedido.arquivo}.html${pedido.ancora ? '#' + pedido.ancora : ''}` : ''

  return (
    <div className="flex h-full flex-col md:flex-row">
      {/* Lista */}
      <aside
        className={`${atual ? 'hidden md:flex' : 'flex'} min-h-0 flex-1 flex-col border-r md:w-[400px] md:flex-none lg:w-[440px]`}
      >
        <header className="space-y-3 border-b px-4 pb-3 pt-4">
          <div className="flex items-baseline justify-between gap-2">
            <h1 className="serif text-xl font-bold leading-tight">Biblioteca de normas</h1>
            <span className="text-xs tabular-nums text-muted-foreground">
              {normas ? `${filtradas.length} de ${normas.length}` : ''}
            </span>
          </div>
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={busca}
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Número, nome ou assunto"
              aria-label="Buscar normas"
              className="h-10 bg-card pl-8 pr-8 text-base md:text-sm"
            />
            {q && (
              <button
                aria-label="Limpar busca"
                onClick={() => setQ('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <Segmentado rotulo="Esfera" valor={esfera} mudar={setEsfera}
              opcoes={[['todas', 'Todas'], ['federal', 'Federal'], ['estadual', 'Estadual (PR)']]} />
            <Segmentado rotulo="Situação" valor={situacao} mudar={setSituacao}
              opcoes={[['todas', 'Todas'], ['vigente', 'Vigentes'], ['revogada', 'Revogadas']]} />
          </div>
          <div className="flex flex-wrap gap-1.5" role="group" aria-label="Tipo de norma">
            {presentesTipos.map(([t, c]) => {
              const on = tipos.includes(t)
              return (
                <button
                  key={t}
                  aria-pressed={on}
                  onClick={() => setTipos(on ? tipos.filter((x) => x !== t) : [...tipos, t])}
                  className={`rounded-full border px-2.5 py-0.5 text-xs transition-colors ${
                    on ? 'border-primary bg-accent font-semibold text-accent-foreground' : 'text-muted-foreground hover:border-primary hover:text-foreground'
                  }`}
                >
                  {nomeTipo(t)} <span className="tabular-nums opacity-70">{c}</span>
                </button>
              )
            })}
            {filtrosAtivos ? (
              <button
                onClick={() => { setQ(''); setEsfera('todas'); setSituacao('todas'); setTipos([]) }}
                className="px-1 text-xs text-primary underline-offset-2 hover:underline"
              >
                Limpar filtros
              </button>
            ) : null}
          </div>
        </header>

        <nav className="min-h-0 flex-1 overflow-y-auto" aria-label="Normas">
          {erro && (
            <p className="p-4 text-sm text-destructive">
              Não foi possível carregar o catálogo ({erro}). Rode <code>python scripts/gerar_html.py</code>.
            </p>
          )}
          {!normas && !erro && <p className="p-4 text-sm text-muted-foreground">Carregando…</p>}
          {normas && !filtradas.length && (
            <p className="p-4 text-sm text-muted-foreground">Nenhuma norma corresponde à busca e aos filtros.</p>
          )}
          {grupos.map(([t, ns]) => (
            <section key={t}>
              <h2 className="sticky top-0 z-10 border-b bg-background/95 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground backdrop-blur">
                {nomeTipo(t)} · {ns.length}
              </h2>
              <ul>
                {ns.map((n) => {
                  const ativo = n.arquivo === sel.arquivo
                  return (
                    <li key={n.arquivo}>
                      <a
                        href={`#${n.arquivo}`}
                        onClick={(e) => { e.preventDefault(); abrir(n.arquivo) }}
                        aria-current={ativo ? 'page' : undefined}
                        className={`block border-b border-l-[3px] px-4 py-2.5 transition-colors ${
                          ativo ? 'border-l-primary bg-accent' : 'border-l-transparent hover:bg-muted'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className={`serif text-[15px] font-semibold leading-snug ${ativo ? 'text-accent-foreground' : ''}`}>
                            {n.norma}
                          </span>
                          {n.situacao === 'revogada' && (
                            <Badge variant="destructive" className="shrink-0 px-1.5 py-0 text-[10px] uppercase">Revogada</Badge>
                          )}
                        </div>
                        {n.apelidos.length > 0 && (
                          <div className="mt-0.5 text-xs font-medium text-primary">{n.apelidos.slice(0, 2).join(' · ')}</div>
                        )}
                        <p className="mt-0.5 line-clamp-2 text-[13px] leading-snug text-muted-foreground">{n.ementa}</p>
                      </a>
                    </li>
                  )
                })}
              </ul>
            </section>
          ))}
        </nav>
      </aside>

      {/* Leitor */}
      <main className={`${atual ? 'flex' : 'hidden md:flex'} min-h-0 min-w-0 flex-1 flex-col`}>
        {atual ? (
          <>
            <div className="flex items-center gap-2 border-b bg-card px-2 py-2 md:px-4">
              <Button variant="ghost" size="sm" className="md:hidden" onClick={() => abrir('')} aria-label="Voltar à lista">
                <ArrowLeft className="h-4 w-4" /> Lista
              </Button>
              <div className="min-w-0 flex-1">
                <div className="serif truncate text-sm font-semibold">{atual.norma}</div>
                <div className="truncate text-xs text-muted-foreground">
                  {atual.orgao || nomeTipo(atual.tipo)}{atual.situacao === 'revogada' ? ' · revogada' : ''}
                </div>
              </div>
              <Button asChild variant="outline" size="sm">
                <a href={`${PASTA}/${atual.arquivo}.html`} target="_blank" rel="noopener">
                  <ExternalLink className="h-4 w-4" /> <span className="hidden sm:inline">Nova aba</span>
                </a>
              </Button>
              <Button variant="ghost" size="sm" className="hidden md:inline-flex" onClick={() => abrir('')} aria-label="Fechar documento">
                <X className="h-4 w-4" />
              </Button>
            </div>
            {pronto ? (
            <iframe
              key={recarga}
              ref={quadro}
              {...(doc.html ? { srcDoc: doc.html } : { src })}
              title={atual.norma}
              onLoad={aoCarregar}
              className="min-h-0 w-full flex-1 border-0 bg-background"
            />
            ) : (
              <p className="p-6 text-sm text-muted-foreground">Abrindo…</p>
            )}
          </>
        ) : (
          <div className="flex flex-1 items-center px-10">
            <div className="max-w-md space-y-3">
              <p className="serif text-2xl font-bold leading-snug">Escolha uma norma na lista para ler o texto aqui.</p>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Cada documento abre com os dispositivos recolhidos: use <strong>Expandir tudo</strong> no topo dele
                ou abra capítulo por capítulo. Os links entre normas funcionam dentro deste leitor.
              </p>
              <p className="text-xs text-muted-foreground">Atalho: <kbd className="rounded border px-1">/</kbd> vai para a busca.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
