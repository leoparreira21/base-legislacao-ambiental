// O atributo é lido pelo controlador de <details> das páginas geradas: no modo de
// localização, abrir um artigo não deve expandir também todos os dispositivos irmãos.
export function marcarOcorrencias(doc: Document, ids: string[]) {
  const estados = [...doc.querySelectorAll('details')].map((el) => [el, el.open] as const)
  const alvos = ids.map((id) => doc.getElementById(id)).filter((el): el is HTMLElement => !!el)
  const estilo = doc.createElement('style')
  estilo.textContent = `
    .ocorrencia-consulta:not(details), details.ocorrencia-consulta > summary,
    details.ocorrencia-consulta > .corpo > .texto { background: var(--marca); color: var(--marca-texto); }
    .ocorrencia-consulta > summary a, .ocorrencia-consulta > .corpo > .texto a { color: var(--marca-texto); }
    .ocorrencia-consulta-atual:not(details), details.ocorrencia-consulta-atual > summary {
      outline: 2px solid var(--realce); outline-offset: 2px; border-radius: 3px;
    }
    .ocorrencia-consulta { scroll-margin-top: 80px; }
  `
  doc.head.appendChild(estilo)
  doc.documentElement.dataset.localizarOcorrencias = 'true'
  estados.forEach(([el]) => { el.open = false })
  alvos.forEach((el) => {
    el.classList.add('ocorrencia-consulta')
    for (let p: HTMLElement | null = el; p; p = p.parentElement) {
      if (p.tagName === 'DETAILS') (p as HTMLDetailsElement).open = true
    }
  })
  return () => {
    alvos.forEach((el) => el.classList.remove('ocorrencia-consulta', 'ocorrencia-consulta-atual'))
    // Restaura a leitura que estava aberta antes de ativar o localizador.
    estados.forEach(([el, aberto]) => { el.open = aberto })
    delete doc.documentElement.dataset.localizarOcorrencias
    estilo.remove()
  }
}
