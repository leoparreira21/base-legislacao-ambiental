import { useCallback, useEffect, useMemo, useState } from 'react'
import { ChevronDown, ChevronUp, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import RotuloDispositivo from './RotuloDispositivo'
import { buscarDispositivos } from './consulta'
import type { ParametrosConsulta, Resultado } from './consulta'
import { marcarOcorrencias } from './localizador'

type Props = {
  parametros: ParametrosConsulta
  buscaNoTexto?: boolean
  slug: string
  ancora: string
  documento: Document | null
  ir: (id: string) => void
  fechar: () => void
}

export default function LocalizadorOcorrencias({ parametros, slug, ancora, documento, ir, fechar, buscaNoTexto }: Props) {
  const [resultado, setResultado] = useState<{ chave: string; itens: Resultado[]; erro: string } | null>(null)
  const [tentativa, setTentativa] = useState(0)
  const { q } = parametros
  const chave = JSON.stringify([slug, parametros, tentativa])
  useEffect(() => {
    if (buscaNoTexto) return
    const controle = new AbortController()
    buscarDispositivos(parametros, slug, controle.signal)
      .then((itens) => { if (!controle.signal.aborted) setResultado({ chave, itens, erro: '' }) })
      .catch((e: Error) => { if (!controle.signal.aborted) setResultado({ chave, itens: [], erro: e.message }) })
    return () => controle.abort()
  }, [chave, buscaNoTexto]) // eslint-disable-line react-hooks/exhaustive-deps

  const atual = !buscaNoTexto && resultado?.chave === chave ? resultado : null
  const itens = useMemo(() => atual?.itens ?? [], [atual])
  const disponiveis = useMemo(() => itens.filter((r) => r.dispositivo_id_html && documento?.getElementById(r.dispositivo_id_html)), [itens, documento])
  const ids = useMemo(() => {
    if (!buscaNoTexto) return [...new Set(disponiveis.map((r) => r.dispositivo_id_html!))]
    if (!documento) return []
    const normalizar = (s: string) => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim()
    const termo = normalizar(q)
    const encontrados = new Set<string>()
    for (const trecho of documento.querySelectorAll('main p, main li, main td, main th, main summary')) {
      const alvo = trecho.closest('[id]')
      if (alvo && termo && normalizar(trecho.textContent ?? '').includes(termo)) encontrados.add(alvo.id)
    }
    return [...encontrados]
  }, [buscaNoTexto, documento, q, disponiveis])
  const indice = ids.indexOf(ancora)

  useEffect(() => {
    if (documento && ids.length && indice < 0) ir(ids[0])
  }, [documento, ids, indice, ir])

  useEffect(() => {
    if (!documento || !ids.length) return
    return marcarOcorrencias(documento, ids)
  }, [documento, ids])

  useEffect(() => {
    if (!documento || indice < 0) return
    const el = documento.getElementById(ids[indice])!
    documento.querySelectorAll('.ocorrencia-consulta-atual').forEach((p) => p.classList.remove('ocorrencia-consulta-atual'))
    el.classList.add('ocorrencia-consulta-atual')
    for (let p: HTMLElement | null = el; p; p = p.parentElement) {
      if (p.tagName === 'DETAILS') (p as HTMLDetailsElement).open = true
    }
    // Aguarda os eventos toggle e o reajuste de layout do documento.
    const janela = documento.defaultView
    let frame = 0
    const timer = janela?.setTimeout(() => {
      frame = janela.requestAnimationFrame(() => el.scrollIntoView({ block: 'center' }))
    }, 0)
    return () => { janela?.clearTimeout(timer); if (frame) janela?.cancelAnimationFrame(frame) }
  }, [documento, ids, indice])

  const mover = useCallback((passo: number) => {
    if (ids.length) ir(ids[indice < 0 ? (passo > 0 ? 0 : ids.length - 1) : (indice + passo + ids.length) % ids.length])
  }, [ids, indice, ir])

  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { e.preventDefault(); fechar() }
      else if (e.key === 'F3') { e.preventDefault(); mover(e.shiftKey ? -1 : 1) }
    }
    window.addEventListener('keydown', tecla)
    documento?.addEventListener('keydown', tecla)
    return () => { window.removeEventListener('keydown', tecla); documento?.removeEventListener('keydown', tecla) }
  }, [documento, mover, fechar])

  const carregando = (!buscaNoTexto && !atual) || !documento
  const selecionado = disponiveis.find((r) => r.dispositivo_id_html === ancora)
  return (
    <section aria-label="Localizar ocorrências" className="border-b bg-accent/40 px-3 py-2 text-xs">
      <div className="flex flex-wrap items-center gap-2">
        <span className="min-w-0 flex-1 break-words">Localizar: <strong>“{parametros.q}”</strong></span>
        <span role="status" className="tabular-nums">{carregando ? 'Carregando…' : `${indice + 1} de ${ids.length}`}</span>
        <div className="flex shrink-0 gap-1">
          <Button variant="outline" size="icon" className="h-8 w-8" aria-label="Ocorrência anterior" title="Ocorrência anterior (Shift+F3)" disabled={carregando || !ids.length} onClick={() => mover(-1)}><ChevronUp className="h-4 w-4" /></Button>
          <Button variant="outline" size="icon" className="h-8 w-8" aria-label="Próxima ocorrência" title="Próxima ocorrência (F3)" disabled={carregando || !ids.length} onClick={() => mover(1)}><ChevronDown className="h-4 w-4" /></Button>
          <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Fechar localizador" title="Fechar localizador (Esc)" onClick={fechar}><X className="h-4 w-4" /></Button>
        </div>
      </div>
      {selecionado && <p className="mt-1 text-primary"><RotuloDispositivo rotulo={selecionado.dispositivo_rotulo} /></p>}
      {atual?.erro && <p role="alert" className="mt-1 text-destructive">{atual.erro} <button className="underline" onClick={() => setTentativa((n) => n + 1)}>Tentar novamente</button></p>}
      {!carregando && !atual?.erro && !ids.length && <p className="mt-1">Nenhum dispositivo desta consulta disponível no texto aberto.</p>}
      {!carregando && ids.length < itens.length && ids.length > 0 && <p className="mt-1">{itens.length - ids.length} dispositivo(s) da busca não foram encontrados neste texto.</p>}
    </section>
  )
}
