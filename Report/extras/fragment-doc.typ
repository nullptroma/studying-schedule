// Короткий PDF без полного ГОСТ-титула (фрагмент отчёта, методичка).
#let fragment-doc(
  title: "",
  criterion: "",
  work-title: "Отчёт",
  doc,
) = {
  set page(
    paper: "a4",
    margin: (left: 3cm, right: 1.5cm, top: 2cm, bottom: 2cm),
    numbering: "1",
  )
  set text(font: "Times New Roman", size: 14pt, lang: "ru")
  set par(first-line-indent: 1.25cm, justify: true, leading: 0.65em)
  set heading(numbering: "1.1")
  show figure.where(kind: table): it => {
    set figure.caption(position: top)
    it
  }
  show figure.where(kind: table): set block(breakable: true)

  show heading.where(level: 1): it => {
    set text(size: 16pt, weight: "bold")
    align(center)[#it.body]
    v(0.75em)
    counter(heading).step(level: 2)
  }
  show heading.where(level: 2): it => {
    set text(size: 14pt, weight: "bold")
    v(0.5em)
    it
    v(0.35em)
  }

  [
    #align(center)[
      #text(size: 12pt)[#work-title]
      #v(0.4em)
      #text(size: 11pt, style: "italic")[#criterion]
      #v(0.6em)
      #text(size: 16pt, weight: "bold")[#title]
      #v(1.2em)
    ]
    #doc
  ]
}
