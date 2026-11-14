import { useEffect, useRef, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search, X } from 'lucide-react'

// Faixa da consulta no texto dos dispositivos: usa a API do Worker (D1, busca full-text).
// Só aparece quando a página é servida pelo Worker (há /api); no artefato ou aberta do
// disco ela some sozinha.

type Resultado = {
  legislacao_nome: string
  legislacao_slug: string
  dispositivo_rotulo: string | null
  dispositivo_tipo: string | null
  dispositivo_texto: string | null
  dispositivo_estrutura: string | null
  dispositivo_id_html: string | null
  dispositivo_revogado: number
}

type PorNorma = Resultado & { ocorrencias: number }

type Props = {
  esferaDe: (slug: string) => string | undefined // undefined: norma fora da biblioteca
  nomeDe: (slug: string) => string | undefined
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

// Destaca no trecho as palavras da consulta (sem acento, início de palavra).
function destacar(texto: string, q: string) {
  const termos = semAcento(q)
    .replace(/\b(and|or|not|near)\b/gi, ' ')
    .split(/[^a-z0-9*]+/)
    .map((t) => t.replace(/\*$/, ''))
    .filter((t) => t.length >= 3)
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
  marcas.sort((a, b) => a[0] - b[0])
  const partes: (string | JSX.Element)[] = []
  let pos = 0
  marcas.forEach(([a, b], k) => {
    if (a < pos) return
    partes.push(texto.slice(pos, a), <mark key={k} className="rounded-sm bg-accent text-accent-foreground">{texto.slice(a, b)}</mark>)
    pos = b
  })
  partes.push(texto.slice(pos))
  return partes
}

export default function ConsultaSQL({ esferaDe, nomeDe, abrir, aberto, fechar }: Props) {
  const [q, setQ] = useState('')
  const [feita, setFeita] = useState('')
  const [esfera, setEsfera] = useState('')
  const [tipo, setTipo] = useState('')
  const [vigentes, setVigentes] = useState(true)
  const [res, setRes] = useState<PorNorma[] | null>(null)
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [abertos, setAbertos] = useState<Record<string, Resultado[] | 'carregando'>>({})
  const campo = useRef<HTMLInputElement>(null)

  useEffect(() => { if (fechar) campo.current?.focus() }, []) // só no painel sobreposto

  const parametros = (termo: string) => ({ q: termo, so_vigentes: String(vigentes), ...(tipo ? { tipo } : {}) })

  // Uma linha por norma (agrupada no D1): o número de dispositivos em que a busca aparece
  // e o dispositivo mais relevante. Os demais só são buscados ao abrir a lista da norma.
  const buscar = async (e?: React.FormEvent, termo = q.trim()) => {
    e?.preventDefault()
    if (termo.length < 3) {
      setErro('Digite ao menos 3 letras.')
      setRes(null)
      return
    }
    setCarregando(true)
    setErro('')
    setAbertos({})
    try {
      const p = new URLSearchParams({ ...parametros(termo), agrupar: 'norma', limit: '300' })
      const r = await fetch('/api/buscar?' + p)
      const d = await r.json().catch(() => ({ erro: `Erro ${r.status} no servidor.` }))
      if (!r.ok || d.erro) throw new Error(d.erro || `Erro ${r.status} no servidor.`)
      setRes(d.normas as PorNorma[])
      setFeita(termo)
    } catch (err) {
      setErro((err as Error).message)
      setRes(null)
    } finally {
      setCarregando(false)
    }
  }

  // tipo de dispositivo e "só vigentes" mudam a contagem: refaz a busca feita
  useEffect(() => { if (feita) buscar(undefined, feita) }, [tipo, vigentes]) // eslint-disable-line react-hooks/exhaustive-deps

  const alternarLista = async (slug: string) => {
    if (abertos[slug]) {
      const { [slug]: _, ...resto } = abertos
      setAbertos(resto)
      return
    }
    setAbertos((a) => ({ ...a, [slug]: 'carregando' }))
    try {
      const r = await fetch('/api/buscar?' + new URLSearchParams({ ...parametros(feita), slug }))
      const d = await r.json()
      if (!r.ok || d.erro) throw new Error(d.erro)
      setAbertos((a) => ({ ...a, [slug]: d.resultados as Resultado[] }))
    } catch {
      setAbertos((a) => { const { [slug]: _, ...resto } = a; return resto })
      setErro('Não foi possível listar os dispositivos dessa norma.')
    }
  }

  // esfera filtra aqui; normas que não estão na biblioteca (ex.: comentários) ficam de fora
  const visiveis = (res ?? []).filter((r) => {
    const e = esferaDe(r.legislacao_slug)
    return e !== undefined && (!esfera || e === esfera)
  })
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
              <p className="px-2 pt-1 text-[12px] leading-snug text-foreground/85">{destacar(g[0].dispositivo_texto, feita)}</p>
            )}
            {g.map((x) => (
              <button
                key={x.dispositivo_id_html ?? x.dispositivo_rotulo}
                onClick={() => abrir(x.legislacao_slug, x.dispositivo_id_html ?? '')}
                className={`block w-full rounded px-2 py-1 text-left transition-colors ${ativoEm(x) ? 'bg-accent' : 'hover:bg-muted'}`}
              >
                <span className="flex flex-wrap items-center gap-1.5 text-xs">
                  <span className="font-medium text-primary">{x.dispositivo_rotulo}</span>
                  {revogado(x)}
                </span>
                {g.length === 1 && x.dispositivo_texto && (
                  <span className="mt-0.5 line-clamp-3 block text-[12px] leading-snug text-foreground/85">{destacar(x.dispositivo_texto, feita)}</span>
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
        <form onSubmit={buscar} className="flex gap-1.5" role="search">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="consulta-sql"
              ref={campo}
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Ex.: outorga AND captação"
              aria-label="Texto a buscar nos dispositivos"
              className="h-9 bg-card pl-8 text-base md:text-sm"
            />
          </div>
          <Button type="submit" size="sm" className="h-9" disabled={carregando}>
            {carregando ? 'Buscando…' : 'Buscar'}
          </Button>
        </form>
        <div className="flex flex-wrap items-center gap-1.5">
          <select aria-label="Esfera" value={esfera} onChange={(e) => setEsfera(e.target.value)} className={sel}>
            <option value="">Todas as esferas</option>
            <option value="federal">Federal</option>
            <option value="estadual">Estadual (PR)</option>
          </select>
          <select aria-label="Tipo de dispositivo" value={tipo} onChange={(e) => setTipo(e.target.value)} className={sel}>
            {TIPOS_DISP.map(([v, r]) => <option key={v} value={v}>{r}</option>)}
          </select>
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <input type="checkbox" checked={vigentes} onChange={(e) => setVigentes(e.target.checked)} className="accent-[hsl(var(--primary))]" />
            Só vigentes
          </label>
        </div>
        <p className="text-[11px] leading-snug text-muted-foreground">
          Busca sem acento nas palavras dos dispositivos. Use <code>AND</code>, <code>OR</code>, <code>NOT</code>, aspas para
          expressão exata e <code>*</code> no fim para prefixo (<code>resid*</code>).
        </p>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto" aria-live="polite">
        {erro && <p className="p-4 text-sm text-destructive">{erro}</p>}
        {res && (
          <p className="border-b px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {visiveis.length} norma{visiveis.length === 1 ? '' : 's'} · {totalDispositivos} dispositivo{totalDispositivos === 1 ? '' : 's'}
          </p>
        )}
        {res && !visiveis.length && !erro && (
          <p className="p-4 text-sm text-muted-foreground">Nenhuma norma com “{feita}” nesses filtros.</p>
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
                  <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-xs">
                    {r.dispositivo_rotulo && <span className="font-medium text-primary">{r.dispositivo_rotulo}</span>}
                    {revogado(r)}
                  </div>
                  {r.dispositivo_texto && (
                    <p className="mt-1 line-clamp-3 text-[13px] leading-snug text-foreground/85">{destacar(r.dispositivo_texto, feita)}</p>
                  )}
                  {r.dispositivo_estrutura && (
                    <p className="mt-1 truncate text-[11px] text-muted-foreground" title={r.dispositivo_estrutura}>
                      {nivel(r.dispositivo_estrutura)}
                    </p>
                  )}
                </button>
                {r.ocorrencias > 1 && (
                  <div className="px-4 pb-2">
                    <button
                      onClick={() => alternarLista(r.legislacao_slug)}
                      aria-expanded={!!lista}
                      className="text-xs font-medium text-primary underline-offset-2 hover:underline"
                    >
                      {lista === 'carregando' ? 'Carregando…' : lista ? 'Ocultar a lista' : `Ver os ${r.ocorrencias} dispositivos`}
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
