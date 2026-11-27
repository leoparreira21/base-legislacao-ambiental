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

export type ModoConsulta = 'simples' | 'avancado'

// tipo: tipo de dispositivo (caput, inciso...); tipoNorma, esfera e ano filtram a norma.
// Campos ausentes = sem filtro (a trilha de temas usa só q, tipo e soVigentes).
export type ParametrosConsulta = {
  q: string
  tipo: string
  soVigentes: boolean
  modo?: ModoConsulta
  tipoNorma?: string
  esfera?: string
  ano?: string
}
export type ConsultaPublicada = { parametros: ParametrosConsulta; slugs: string[] }

export function parametrosBusca(p: ParametrosConsulta): Record<string, string> {
  return {
    q: p.q,
    modo: p.modo ?? 'simples',
    ocultar_revogados: String(p.soVigentes),
    ...(p.tipo ? { tipo: p.tipo } : {}),
    ...(p.tipoNorma ? { tipo_norma: p.tipoNorma } : {}),
    ...(p.esfera ? { esfera: p.esfera } : {}),
    ...(p.ano ? { ano: p.ano } : {}),
  }
}

export type OpcaoFiltro = { valor: string | number; total: number }
export type Filtros = { tipos: OpcaoFiltro[]; esferas: OpcaoFiltro[]; anos: OpcaoFiltro[] }

export async function carregarFiltros(): Promise<Filtros | null> {
  try {
    const r = await fetch('/api/filtros')
    if (!r.ok) return null
    const d = await r.json()
    return Array.isArray(d?.tipos) ? d : null
  } catch {
    return null
  }
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
