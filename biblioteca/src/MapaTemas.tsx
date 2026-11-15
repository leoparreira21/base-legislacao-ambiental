import { useMemo, useRef, useState } from 'react'
import { Network } from 'lucide-react'
import { Button } from '@/components/ui/button'
import './mapa-temas.css'

type Norma = { arquivo: string; norma: string; situacao: string; temas?: Record<string, string> }
const chave = (s: string) => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/[-\s]+/g, ' ').trim()
const pontos = [[18,16],[82,16],[82,50],[82,84],[18,84],[18,50]]

export default function MapaTemas({ inicial, normas, abrir }: {
  inicial: Norma; normas: Norma[]; abrir: (arquivo: string, ancora: string, tema: string, ancoraOrigem: string) => void
}) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [ativo, setAtivo] = useState(false)
  const [bases, setBases] = useState([inicial.arquivo])
  const [tema, setTema] = useState('')
  const [busca, setBusca] = useState('')
  const [pagina, setPagina] = useState(0)
  const indice = useMemo(() => {
    const mapa = new Map<string, Map<string, { nome: string; ancora: string }>>()
    if (ativo) for (const n of normas) {
      const termos = new Map<string, { nome: string; ancora: string }>()
      for (const [nome, ancora] of Object.entries(n.temas ?? {})) {
        const k = chave(nome)
        if (!termos.has(k) || ancora) termos.set(k, { nome: nome.replaceAll('-', ' '), ancora })
      }
      mapa.set(n.arquivo, termos)
    }
    return mapa
  }, [normas, ativo])
  const entradas = indice.get(inicial.arquivo)
  const temas = [...(entradas?.keys() ?? [])].filter(k => bases.every(b => indice.get(b)?.has(k)))
  const relacionadas = normas.filter(n => !bases.includes(n.arquivo) && indice.get(n.arquivo)?.has(tema))
  const nos = (tema ? relacionadas.map(n => ({ id: n.arquivo, nome: n.norma + (n.situacao === 'revogada' ? ' · revogada' : '') }))
    : temas.map(k => ({ id: k, nome: entradas!.get(k)!.nome })))
    .filter(n => chave(n.nome).includes(chave(busca))).sort((a,b) => a.nome.localeCompare(b.nome,'pt-BR'))
  function selecionar(t: string) { setTema(t); setBusca(''); setPagina(0) }
  function mudarBases(lista: string[]) { setBases(lista); selecionar('') }
  const visiveis = nos.slice(pagina * 6, pagina * 6 + 6)
  const centro = tema ? entradas?.get(tema)?.nome : bases.length === 1 ? inicial.norma : bases.length + ' normas em comum'
  return <>
    <Button variant="outline" size="sm" onClick={() => { setAtivo(true); dialog.current?.showModal() }}><Network size={16}/> Temas</Button>
    <dialog ref={dialog} className="mapa-temas" aria-label="Mapa de temas" onClose={() => setAtivo(false)}>
      {ativo && <>
        <header><h2>Mapa de temas</h2><Button variant="outline" size="sm" onClick={() => dialog.current?.close()}>Fechar</Button></header>
        <div className="mt-bases"><strong>{inicial.norma}</strong>
          {bases.slice(1).map(b => <button key={b} onClick={() => mudarBases(bases.filter(id => id !== b))} aria-label={'Remover '+normas.find(n=>n.arquivo===b)?.norma}>{normas.find(n=>n.arquivo===b)?.norma} ×</button>)}
        </div>
        <select aria-label="Adicionar norma para comparar" value="" onChange={e => mudarBases([...bases,e.target.value])}>
          <option value="">Adicionar norma para comparar…</option>
          {normas.filter(n => !bases.includes(n.arquivo)).map(n => <option key={n.arquivo} value={n.arquivo}>{n.norma}</option>)}
        </select>
        <div className="mt-tools">{tema && <Button variant="outline" size="sm" onClick={() => selecionar('')}>← Temas</Button>}
          <label>{tema ? 'Normas relacionadas' : bases.length > 1 ? 'Temas em comum' : 'Temas da norma'}
            <input type="search" aria-label="Filtrar nós" placeholder={tema ? 'Filtrar normas…' : 'Filtrar temas…'} value={busca} onChange={e=>{setBusca(e.target.value);setPagina(0)}}/>
          </label>
        </div>
        {visiveis.length > 0 ? <div className="mt-rede">
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">{visiveis.map((n,i)=><line key={n.id} x1="50" y1="50" x2={pontos[i][0]} y2={pontos[i][1]}/>)}</svg>
          <strong className="mt-centro">{centro}</strong>
          {visiveis.map((n,i)=><button key={n.id} className="mt-no" style={{left:pontos[i][0]+'%',top:pontos[i][1]+'%'}} onClick={()=>{
            if (!tema) selecionar(n.id)
            else { dialog.current?.close(); abrir(n.id, indice.get(n.id)?.get(tema)?.ancora ?? '', entradas!.get(tema)!.nome, entradas!.get(tema)!.ancora) }
          }}>{n.nome}</button>)}
        </div> : <p className="mt-vazio">{busca ? 'Nenhum resultado para este filtro.' : tema ? 'Nenhuma outra norma do catálogo contém este tema.' : 'Nenhum tema encontrado para esta seleção.'}</p>}
        <footer><span aria-live="polite">{nos.length} {tema ? 'normas' : 'temas'}</span>{nos.length>6 && <>
          <button disabled={!pagina} onClick={()=>setPagina(pagina-1)}>Anterior</button>
          <span>{pagina+1} / {Math.ceil(nos.length/6)}</span>
          <button disabled={(pagina+1)*6>=nos.length} onClick={()=>setPagina(pagina+1)}>Próxima</button></>}</footer>
      </>}
    </dialog>
  </>
}
