// Abrevia apenas a referência exibida; o texto normativo e seus IDs permanecem iguais.
export default function RotuloDispositivo({ rotulo }: { rotulo: string | null }) {
  const partes = (rotulo ?? '').split(/,\s*/).flatMap((parte) => {
    if (/^caput$/i.test(parte)) return []
    const alinea = parte.match(/^al[ií]nea\s+["“']?([a-z](?:-[a-z])?)["”']?$/i)
    if (alinea) return [{ texto: alinea[1], italico: true }]
    const texto = parte.replace(/^par[aá]grafo\s+[uú]nico$/i, '§ único').replace(/^(?:inciso|item)\s+/i, '')
    return texto ? [{ texto, italico: false }] : []
  })
  return <>{partes.map((parte, i) => <span key={i}>{i > 0 && ', '}{parte.italico ? <i>{parte.texto}</i> : parte.texto}</span>)}</>
}
