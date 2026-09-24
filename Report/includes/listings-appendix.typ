// Стили листингов; gen_listings.py вставляет этот файл в generated/appendix-a.typ.

#show raw: set text(font: "DejaVu Sans Mono")

#let pz-listing-num-outset = 30mm
#let pz-listing-code-indent = 1.25cm

#show figure.where(supplement: [Листинг]): set block(breakable: true)

#show raw.where(block: true): it => block(
  breakable: true,
  width: 100% + pz-listing-num-outset,
  outset: (left: pz-listing-num-outset),
)[
  #set block(spacing: 0pt)
  #it
]

#show raw.line: it => grid(
  columns: (1.5em, 1fr),
  column-gutter: pz-listing-code-indent,
  align: (right + horizon, left + horizon),
  inset: (y: 0.35pt),
  text(size: 8.5pt, fill: luma(120))[#str(it.number)],
  box(width: 100%)[
    #set text(size: 9pt)
    #set par(leading: 0.45em)
    #it.body
  ],
)

#set figure(gap: 0.35em)
