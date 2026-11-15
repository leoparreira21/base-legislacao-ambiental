export type Resultado = {
  legislacao_nome: string
  legislacao_slug: string
  legislacao_ementa: string | null
  dispositivo_rotulo: string | null
  dispositivo_tipo: string | null
  dispositivo_texto: string | null
  dispositivo_estrutura: string | null
  dispositivo_id_html: string | null
  dispositivo_revogado: number
}

export type ParametrosConsulta = { q: string; tipo: string; soVigentes: boolean }
export type ConsultaPublicada = { parametros: ParametrosConsulta; slugs: string[] }

export function parametrosBusca(p: ParametrosConsulta) {
  return { q: p.q, so_vigentes: String(p.soVigentes), ...(p.tipo ? { tipo: p.tipo } : {}) }
}

export async function buscarDispositivos(p: ParametrosConsulta, slug: string, signal: AbortSignal): Promise<Resultado[]> {
  const itens: Resultado[] = []
  let offset = 0
  for (;;) {
    const r = await fetch('/api/buscar?' + new URLSearchParams({ ...parametrosBusca(p), slug, offset: String(offset) }), { signal })
    const d = await r.json().catch(() => ({ erro: `Erro ${r.status} no servidor.` }))
    if (!r.ok || d.erro || !Array.isArray(d.resultados)) throw new Error(d.erro || 'Não foi possível listar os dispositivos dessa norma.')
    itens.push(...d.resultados)
    if (d.proximo_offset == null) return itens
    if (!Number.isSafeInteger(d.proximo_offset) || d.proximo_offset <= offset || !d.resultados.length) throw new Error('Não foi possível continuar a lista de dispositivos.')
    offset = d.proximo_offset
  }
}
