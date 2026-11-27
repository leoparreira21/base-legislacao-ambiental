import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search, X } from 'lucide-react'
import type { ReactNode } from 'react'
import RotuloDispositivo from './RotuloDispositivo'
import { buscarDispositivos, carregarFiltros, parametrosBusca } from './consulta'
import type { ConsultaPublicada, Filtros, ModoConsulta, ParametrosConsulta, Resultado } from './consulta'

// Faixa da consulta no texto dos dispositivos: usa a API do Worker (D1, busca full-text).
// Só aparece quando a página é servida pelo Worker (há /api); no artefato ou aberta do
// disco ela some sozinha.

type PorNorma = Resultado & { ocorrencias: number }

type Props = {
  esferaDe: (slug: string) => string | undefined // undefined: norma fora da biblioteca
  nomeDe: (slug: string) => string | undefined
  ementaDe: (slug: string) => string | undefined
  publicarConsulta: (consulta: ConsultaPublicada | null) => void
  abrir: (slug: string, ancora: string) => void
  aberto: { arquivo: string; ancora: string }
  fechar?: () => void
}

const TIPOS_DISP: [string, string][] = [
  ['', 'Qualquer dispositivo'],
  ['ementa', 'Ementa'],
  ['caput', 'Caput de artigo'],
  ['paragrafo', 'Parágrafo'],
  ['paragrafo_unico', 'Parágrafo único'],
  ['inciso', 'Inciso'],
  ['alinea', 'Alínea'],
]

// tipo_norma já vem do D1 com o nome de exibição ("IN IAT", "Resolução CEMA")
type Operador = 'OR' | 'AND' | 'NOT' | 'near' | 'aspas' | '*'
const OPERADORES: [Operador, string, string][] = [
  ['OR', 'OR', 'qualquer um dos termos'],
  ['AND', 'AND', 'todos os termos'],
  ['NOT', 'NOT', 'exclui o termo seguinte (não pode iniciar a consulta)'],
  ['near', 'NEAR( , 10)', 'termos a até 10 palavras um do outro'],
  ['aspas', '" "', 'expressão exata'],
  ['*', '*', 'prefixo: resid* acha resíduo, resíduos, residencial…'],
]

const nomeEsfera = (v: string) => (v === 'estadual' ? 'Estadual (PR)' : v.charAt(0).toUpperCase() + v.slice(1))

const AJUDA: Record<ModoConsulta, ReactNode> = {
  simples: <>Digite as palavras, sem se preocupar com acento ou plural. Aparecem os dispositivos com qualquer uma
    delas; os que trazem a expressão inteira vêm primeiro.</>,
  avancado: <>Combine com <code>AND</code>, <code>OR</code>, <code>NOT</code> (em maiúsculas), <code>NEAR(a b, 10)</code>{' '}
    para palavras próximas, aspas para expressão exata, <code>*</code> para prefixo (<code>resid*</code>) e parênteses.</>,
}

export async function apiDisponivel(): Promise<boolean> {
  if (!location.protocol.startsWith('http')) return false
  try {
    const r = await fetch('/api', { headers: { accept: 'application/json' } })
    if (!r.ok) return false
    const d = await r.json()
    return !!d?.endpoints
  } catch {
    return false
  }
}

const semAcento = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

// Destaca no trecho os termos que a API usou na consulta (sem acento, início de palavra;
// frases entram inteiras). Sem termos da API, usa as palavras digitadas.
function destacar(texto: string, lista: string[]) {
  const termos = [...new Set(lista.map((t) => semAcento(t).replace(/\*$/, '').trim()))]
    .filter((t) => t.length >= 2)
    .sort((a, b) => b.length - a.length) // frase antes das palavras soltas
  if (!termos.length) return texto
  const base = semAcento(texto)
  const marcas: [number, number][] = []
  termos.forEach((t) => {
    let i = base.indexOf(t)
    while (i >= 0) {
      if (i === 0 || !/[a-z0-9]/.test(base[i - 1])) marcas.push([i, i + t.length])
      i = base.indexOf(t, i + t.length)
    }
  })
  if (!marcas.length) return texto
  marcas.sort((a, b) => a[0] - b[0] || b[1] - a[1])
  const partes: ReactNode[] = []
  let pos = 0
  marcas.forEach(([a, b], k) => {
    if (a < pos) return
    partes.push(texto.slice(pos, a), <mark key={k} className="brand-highlight rounded-sm">{texto.slice(a, b)}</mark>)
    pos = b
  })
  partes.push(texto.slice(pos))
  return partes
}

export default function ConsultaSQL({ esferaDe, nomeDe, ementaDe, publicarConsulta, abrir, aberto, fechar }: Props) {
  const [q, setQ] = useState('')
  const [modo, setModo] = useState<ModoConsulta>('simples')
  const [feita, setFeita] = useState<ParametrosConsulta | null>(null)
  const [termos, setTermos] = useState<string[]>([])
  const [esfera, setEsfera] = useState('')
  const [tipoNorma, setTipoNorma] = useState('')
  const [ano, setAno] = useState('')
  const [tipo, setTipo] = useState('')
  const [vigentes, setVigentes] = useState(true)
  const [opcoes, setOpcoes] = useState<Filtros | null>(null)
  const [res, setRes] = useState<PorNorma[] | null>(null)
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [abertos, setAbertos] = useState<Record<string, Resultado[] | 'carregando'>>({})
  const campo = useRef<HTMLInputElement>(null)
  const requisicao = useRef<AbortController | null>(null)
  const termoConsultado = useRef('')
  const listas = useRef(new Map<string, AbortController>())

  useEffect(() => () => {
    requisicao.current?.abort()
    listas.current.forEach((c) => c.abort())
  }, [])

  useEffect(() => { if (fechar) campo.current?.focus() }, []) // só no painel sobreposto
  useEffect(() => { carregarFiltros().then(setOpcoes) }, [])

  // Botões dos operadores (só no modo avançado): inserem no cursor ou em volta do trecho selecionado.
  const inserirOperador = (op: Operador) => {
    const el = campo.current
    const ini = el?.selectionStart ?? q.length
    const fim = el?.selectionEnd ?? q.length
    const antes = q.slice(0, ini), sel = q.slice(ini, fim), depois = q.slice(fim)
    const sep = (t: string) => (t && !/\s$/.test(t) ? ' ' : '')
    let novo: string, cursorIni: number, cursorFim: number
    if (op === 'aspas' || op === 'near') {
      const [abre, fecha] = op === 'aspas' ? ['"', '"'] : ['NEAR(', ', 10)']
      const pre = antes + sep(antes) + abre
      novo = pre + sel + fecha + (depois && !/^\s/.test(depois) ? ' ' : '') + depois
      cursorIni = pre.length
      cursorFim = pre.length + sel.length
    } else if (op === '*') {
      novo = antes + sel + '*' + depois
      cursorIni = cursorFim = ini + sel.length + 1
    } else {
      const pre = antes.replace(/\s+$/, '') + (antes.trim() ? ' ' : '') + op + ' '
      novo = pre + sel + depois.replace(/^\s+/, '')
      cursorIni = pre.length
      cursorFim = pre.length + sel.length
    }
    cursorPendente.current = [cursorIni, cursorFim]
    setQ(novo)
  }
  // posiciona o cursor logo depois que o campo recebe o texto novo
  const cursorPendente = useRef<[number, number] | null>(null)
  useLayoutEffect(() => {
    const c = cursorPendente.current
    if (!c || !campo.current) return
    cursorPendente.current = null
    campo.current.focus()
    campo.current.setSelectionRange(c[0], c[1])
  }, [q])

  const parametros = (termo: string): ParametrosConsulta => ({ q: termo, modo, soVigentes: vigentes, tipo, tipoNorma, esfera, ano })

  // Uma linha por norma (agrupada no D1): o número de dispositivos em que a busca aparece
  // e o dispositivo mais relevante. Os demais só são buscados ao abrir a lista da norma.
  const buscar = async (e?: React.FormEvent, termo = q.trim()) => {
    e?.preventDefault()
    requisicao.current?.abort()
    listas.current.forEach((c) => c.abort())
    listas.current.clear()
    publicarConsulta(null)
    if (!termo || (modo === 'simples' && !/[\p{L}\p{N}]{2}/u.test(termo))) {
      termoConsultado.current = ''
      setErro('Digite ao menos uma palavra com 2 letras ou mais.')
      setRes(null)
      setCarregando(false)
      return
    }
    setCarregando(true)
    termoConsultado.current = termo
    setRes(null)
    setErro('')
    setAbertos({})
    const controle = new AbortController()
    requisicao.current = controle
    try {
      const p = new URLSearchParams({ ...parametrosBusca(parametros(termo)), agrupar: 'norma', limit: '300' })
      const r = await fetch('/api/buscar?' + p, { signal: controle.signal })
      const d = await r.json().catch(() => ({ erro: `Erro ${r.status} no servidor.` }))
      if (!r.ok || d.erro) throw new Error([d.erro || `Erro ${r.status} no servidor.`, d.dica].filter(Boolean).join(' '))
      if (controle.signal.aborted) return
      setRes(d.normas as PorNorma[])
      setFeita(parametros(termo))
      setTermos(Array.isArray(d.termos) && d.termos.length ? d.termos : termo.split(/\s+/))
      publicarConsulta({ parametros: parametros(termo), slugs: d.normas.map((n: PorNorma) => n.legislacao_slug) })
    } catch (err) {
      if (controle.signal.aborted) return
      setErro((err as Error).message)
      setRes(null)
    } finally {
      if (!controle.signal.aborted) setCarregando(false)
    }
  }

  // modo e filtros mudam a contagem: refaz a busca feita
  useEffect(() => {
    if (termoConsultado.current) buscar(undefined, termoConsultado.current)
  }, [modo, tipo, vigentes, tipoNorma, esfera, ano]) // eslint-disable-line react-hooks/exhaustive-deps

  const alternarLista = async (slug: string) => {
    if (abertos[slug]) {
      listas.current.get(slug)?.abort()
      listas.current.delete(slug)
      const { [slug]: _, ...resto } = abertos
      setAbertos(resto)
      return
    }
    setAbertos((a) => ({ ...a, [slug]: 'carregando' }))
    const controle = new AbortController()
    listas.current.set(slug, controle)
    try {
      const itens = await buscarDispositivos(feita ?? parametros(q.trim()), slug, controle.signal)
      if (!controle.signal.aborted) setAbertos((a) => ({ ...a, [slug]: itens }))
    } catch {
      if (controle.signal.aborted) return
      setAbertos((a) => { const { [slug]: _, ...resto } = a; return resto })
      setErro('Não foi possível listar os dispositivos dessa norma.')
    } finally {
      if (listas.current.get(slug) === controle) listas.current.delete(slug)
    }
  }

  // normas que não estão na biblioteca (ex.: comentários) ficam de fora
  const visiveis = (res ?? []).filter((r) => esferaDe(r.legislacao_slug) !== undefined)
  const filtrosAtivos = !!(esfera || tipoNorma || ano || tipo || !vigentes)
  const limparFiltros = () => { setEsfera(''); setTipoNorma(''); setAno(''); setTipo(''); setVigentes(true) }
  const totalDispositivos = visiveis.reduce((s, r) => s + r.ocorrencias, 0)

  // da estrutura (Capítulo > Seção > Subseção) mostra o nível mais próximo do dispositivo
  const nivel = (e: string | null) => (e ? e.split(' > ').pop() ?? e : '')

  const ativoEm = (x: Resultado) => aberto.arquivo === x.legislacao_slug && aberto.ancora === (x.dispositivo_id_html ?? '')
  const revogado = (x: Resultado) =>
    x.dispositivo_revogado ? (
      <span className="rounded bg-destructive px-1 text-[10px] font-semibold uppercase text-destructive-foreground">Revogado</span>
    ) : null

  // Lista dos dispositivos de uma norma; textos idênticos (ex.: a alínea "j" dos arts. 19,
  // 34, 42 e 46 da IN IAT 28/2026) aparecem uma vez, com os dispositivos lado a lado.
  const listaDaNorma = (itens: Resultado[]) => {
    const grupos: Resultado[][] = []
    const porTexto = new Map<string, Resultado[]>()
    itens.forEach((r) => {
      const chave = (r.dispositivo_texto ?? r.dispositivo_id_html ?? '').trim()
      const g = porTexto.get(chave)
      if (g) g.push(r)
      else { const n = [r]; porTexto.set(chave, n); grupos.push(n) }
    })
    return (
      <ul className="mt-1.5 space-y-1 border-l-2 pl-2">
        {grupos.map((g) => (
          <li key={g[0].dispositivo_id_html ?? g[0].dispositivo_rotulo}>
            {g.length > 1 && g[0].dispositivo_texto && (
              <p className="px-2 pt-1 text-[12px] leading-snug text-foreground/85">{destacar(g[0].dispositivo_texto, termos)}</p>
            )}
            {g.map((x) => (
              <button
                key={x.dispositivo_id_html ?? x.dispositivo_rotulo}
                onClick={() => abrir(x.legislacao_slug, x.dispositivo_id_html ?? '')}
                className={`block w-full rounded px-2 py-1 text-left transition-colors ${ativoEm(x) ? 'bg-accent' : 'hover:bg-muted'}`}
              >
                <span className="flex flex-wrap items-center gap-1.5 text-xs">
                  <span className="font-medium text-primary"><RotuloDispositivo rotulo={x.dispositivo_rotulo} /></span>
                  {revogado(x)}
                </span>
                {g.length === 1 && x.dispositivo_texto && (
                  <span className="mt-0.5 line-clamp-3 block text-[12px] leading-snug text-foreground/85">{destacar(x.dispositivo_texto, termos)}</span>
                )}
                {x.dispositivo_estrutura && (
                  <span className="block truncate text-[11px] text-muted-foreground" title={x.dispositivo_estrutura}>
                    {nivel(x.dispositivo_estrutura)}
                  </span>
                )}
              </button>
            ))}
          </li>
        ))}
      </ul>
    )
  }

  const sel = 'h-8 rounded-md border bg-card px-2 text-xs text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring'

  return (
    <div className="flex h-full min-h-0 flex-col">
      <header className="space-y-2.5 border-b px-4 pb-3 pt-4">
        <div className="flex items-baseline justify-between gap-2">
          <h2 className="serif text-lg font-bold leading-tight">Consulta no texto</h2>
          {fechar && (
            <button onClick={fechar} aria-label="Fechar consulta" className="rounded p-1 text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <div role="group" aria-label="Tipo de consulta" className="inline-flex rounded-md border bg-card p-0.5 text-xs">
          {(['simples', 'avancado'] as const).map((m) => (
            <button
              key={m}
              type="button"
              aria-pressed={modo === m}
              onClick={() => setModo(m)}
              className={`rounded px-2.5 py-1 font-medium transition-colors ${modo === m ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            >
              {m === 'simples' ? 'Simples' : 'Avançada'}
            </button>
          ))}
        </div>
        <form noValidate onSubmit={buscar} className="flex gap-1.5" role="search">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="consulta-sql"
              ref={campo}
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={modo === 'simples' ? 'Ex.: resíduos sólidos' : 'Ex.: outorga AND NEAR(captação água, 5)'}
              aria-label="Texto a buscar nos dispositivos"
              className="h-9 bg-card pl-8 pr-8 text-base md:text-sm"
            />
            {q && <button type="button" aria-label="Limpar consulta no texto" onClick={() => {
              requisicao.current?.abort()
              listas.current.forEach((c) => c.abort())
              listas.current.clear()
              termoConsultado.current = ''
              setQ(''); setFeita(null); setTermos([]); setRes(null); setAbertos({}); setErro(''); setCarregando(false)
              publicarConsulta(null)
              campo.current?.focus()
            }} className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></button>}
          </div>
          <Button type="submit" size="sm" className="h-9" disabled={carregando}>
            {carregando ? 'Buscando…' : 'Buscar'}
          </Button>
        </form>
        {modo === 'avancado' && <div role="toolbar" aria-label="Operadores da consulta avançada" className="flex flex-wrap gap-1">
          {OPERADORES.map(([op, rotulo, dica]) => (
            <button
              key={op}
              type="button"
              title={`${rotulo}: ${dica}`}
              aria-label={`Inserir ${rotulo}: ${dica}`}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => inserirOperador(op)}
              className="rounded border bg-card px-2 py-0.5 font-mono text-xs font-semibold text-foreground transition-colors hover:border-primary hover:text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring"
            >
              {rotulo}
            </button>
          ))}
        </div>}
        <div className="grid grid-cols-2 gap-1.5">
          <select aria-label="Tipo de norma" value={tipoNorma} onChange={(e) => setTipoNorma(e.target.value)} className={`${sel} col-span-2`}>
            <option value="">Todos os tipos de norma</option>
            {(opcoes?.tipos ?? []).map((o) => <option key={o.valor} value={o.valor}>{o.valor} ({o.total})</option>)}
          </select>
          <select aria-label="Esfera" value={esfera} onChange={(e) => setEsfera(e.target.value)} className={sel}>
            <option value="">Todas as esferas</option>
            {(opcoes?.esferas.length ? opcoes.esferas : [{ valor: 'federal', total: 0 }, { valor: 'estadual', total: 0 }]).map((o) => (
              <option key={o.valor} value={o.valor}>{nomeEsfera(String(o.valor))}{o.total ? ` (${o.total})` : ''}</option>
            ))}
          </select>
          <select aria-label="Ano" value={ano} onChange={(e) => setAno(e.target.value)} className={sel}>
            <option value="">Qualquer ano</option>
            {(opcoes?.anos ?? []).map((o) => <option key={o.valor} value={o.valor}>{o.valor} ({o.total})</option>)}
          </select>
          <select aria-label="Tipo de dispositivo" value={tipo} onChange={(e) => setTipo(e.target.value)} className={`${sel} col-span-2`}>
            {TIPOS_DISP.map(([v, r]) => <option key={v} value={v}>{r}</option>)}
          </select>
        </div>
        <div className="flex items-center justify-between gap-2">
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <input type="checkbox" checked={vigentes} onChange={(e) => setVigentes(e.target.checked)} className="accent-[hsl(var(--primary))]" />
            Ocultar revogados
          </label>
          {filtrosAtivos && (
            <button type="button" onClick={limparFiltros} className="text-xs font-medium text-primary underline-offset-2 hover:underline">
              Limpar filtros
            </button>
          )}
        </div>
        <p className="text-[11px] leading-snug text-muted-foreground">{AJUDA[modo]}</p>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto" aria-live="polite">
        {erro && <p className="p-4 text-sm text-destructive">{erro}</p>}
        {res && (
          <p className="border-b px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {visiveis.length} norma{visiveis.length === 1 ? '' : 's'} · {totalDispositivos} dispositivo{totalDispositivos === 1 ? '' : 's'}
          </p>
        )}
        {res && !visiveis.length && !erro && (
          <p className="p-4 text-sm text-muted-foreground">
            Nenhuma norma com “{feita?.q}”{filtrosAtivos ? ' nesses filtros' : ''}.
            {modo === 'avancado' && ' Confira os operadores ou tente a consulta simples.'}
          </p>
        )}
        {!res && !erro && (
          <p className="p-4 text-sm leading-relaxed text-muted-foreground">
            Procura a expressão dentro de artigos, parágrafos, incisos e alíneas de todas as normas. Cada norma aparece uma
            vez, com o número de dispositivos em que a expressão aparece. Clique para abrir a norma no trecho mais relevante.
          </p>
        )}
        <ul>
          {visiveis.map((r) => {
            const lista = abertos[r.legislacao_slug]
            return (
              <li key={r.legislacao_slug} className={`border-b border-l-[3px] ${aberto.arquivo === r.legislacao_slug ? 'border-l-primary' : 'border-l-transparent'}`}>
                <button
                  onClick={() => abrir(r.legislacao_slug, r.dispositivo_id_html ?? '')}
                  className={`block w-full px-4 pb-1.5 pt-2.5 text-left transition-colors ${ativoEm(r) ? 'bg-accent' : 'hover:bg-muted'}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="serif text-[13px] font-semibold leading-snug">{nomeDe(r.legislacao_slug) ?? r.legislacao_nome}</span>
                    <span
                      className="shrink-0 rounded-full bg-secondary px-2 py-0.5 text-[11px] font-semibold tabular-nums text-secondary-foreground"
                      title="Dispositivos desta norma em que a busca aparece"
                    >
                      {r.ocorrencias} {r.ocorrencias === 1 ? 'ocorrência' : 'ocorrências'}
                    </span>
                  </div>
                  <p className="mt-1 text-[13px] leading-snug text-muted-foreground">{ementaDe(r.legislacao_slug) || r.legislacao_ementa || 'Súmula não informada.'}</p>
                </button>
                {r.ocorrencias > 0 && (
                  <div className="px-4 pb-2">
                    <button
                      onClick={() => alternarLista(r.legislacao_slug)}
                      aria-expanded={!!lista}
                      className="text-xs font-medium text-primary underline-offset-2 hover:underline"
                    >
                      {lista === 'carregando' ? 'Carregando…' : lista ? 'Ocultar a lista' : r.ocorrencias === 1 ? 'Ver o dispositivo' : `Ver os ${r.ocorrencias} dispositivos`}
                    </button>
                    {lista && lista !== 'carregando' && listaDaNorma(lista)}
                  </div>
                )}
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
