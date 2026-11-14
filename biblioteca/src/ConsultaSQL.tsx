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

type Props = {
  esferaDe: (slug: string) => string | undefined
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
  const [res, setRes] = useState<Resultado[] | null>(null)
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const campo = useRef<HTMLInputElement>(null)

  useEffect(() => { if (fechar) campo.current?.focus() }, []) // só no painel sobreposto

  const buscar = async (e?: React.FormEvent) => {
    e?.preventDefault()
    const termo = q.trim()
    if (termo.length < 3) {
      setErro('Digite ao menos 3 letras.')
      setRes(null)
      return
    }
    setCarregando(true)
    setErro('')
    try {
      const p = new URLSearchParams({ q: termo, limit: '100', so_vigentes: String(vigentes) })
      const r = await fetch('/api/buscar?' + p)
      const d = await r.json().catch(() => ({ erro: `Erro ${r.status} no servidor.` }))
      if (!r.ok || d.erro) throw new Error(d.erro || `Erro ${r.status} no servidor.`)
      setRes(d.resultados as Resultado[])
      setFeita(termo)
    } catch (err) {
      setErro((err as Error).message)
      setRes(null)
    } finally {
      setCarregando(false)
    }
  }

  // esfera e tipo de dispositivo filtram aqui, sobre os 100 mais relevantes
  const visiveis = (res ?? []).filter(
    (r) => (!esfera || esferaDe(r.legislacao_slug) === esfera) && (!tipo || r.dispositivo_tipo === tipo),
  )

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
            {visiveis.length} de {res.length} dispositivo{res.length === 1 ? '' : 's'}
            {res.length === 100 ? ' (os 100 mais relevantes)' : ''}
          </p>
        )}
        {res && !visiveis.length && !erro && (
          <p className="p-4 text-sm text-muted-foreground">Nenhum dispositivo com “{feita}” nesses filtros.</p>
        )}
        {!res && !erro && (
          <p className="p-4 text-sm leading-relaxed text-muted-foreground">
            Procura a expressão dentro de artigos, parágrafos, incisos e alíneas de todas as normas. Clique num resultado
            para abrir a norma já no dispositivo.
          </p>
        )}
        <ul>
          {visiveis.map((r, i) => {
            const ativo = aberto.arquivo === r.legislacao_slug && aberto.ancora === (r.dispositivo_id_html ?? '')
            return (
              <li key={i}>
                <button
                  onClick={() => abrir(r.legislacao_slug, r.dispositivo_id_html ?? '')}
                  className={`block w-full border-b border-l-[3px] px-4 py-2.5 text-left transition-colors ${
                    ativo ? 'border-l-primary bg-accent' : 'border-l-transparent hover:bg-muted'
                  }`}
                >
                  <div className="serif text-[13px] font-semibold leading-snug">
                    {nomeDe(r.legislacao_slug) ?? r.legislacao_nome}
                  </div>
                  <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-xs">
                    {r.dispositivo_rotulo && <span className="font-medium text-primary">{r.dispositivo_rotulo}</span>}
                    {r.dispositivo_revogado ? (
                      <span className="rounded bg-destructive px-1 text-[10px] font-semibold uppercase text-destructive-foreground">Revogado</span>
                    ) : null}
                  </div>
                  {r.dispositivo_texto && (
                    <p className="mt-1 line-clamp-4 text-[13px] leading-snug text-foreground/85">
                      {destacar(r.dispositivo_texto, feita)}
                    </p>
                  )}
                  {r.dispositivo_estrutura && (
                    <p className="mt-1 truncate text-[11px] text-muted-foreground">{r.dispositivo_estrutura}</p>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
