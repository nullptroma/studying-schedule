// Таблицы – как в «Пример работы с Typst.typ» и gost: figure + table + table.header.
// ГОСТ 7.32 / чек-лист: в тексте и подписях – среднее тире «–» (U+2013), не длинное «—».
#let pz-figure-caption-separator = [#sym.space.nobreak#sym.dash.en#sym.space.nobreak]
// Разрыв длинных таблиц и подпись сверху задаёт шаблон modern-g7-32 (style.typ).

#show table: set text(hyphenate: true, lang: "ru")
#show table.cell: set block(inset: (x: 5pt, y: 3pt))

// Таблица внутри figure – по умолчанию один неразрывный block (обрезка длинных реестров).
#show figure.where(kind: table): set block(breakable: true)

#let pz-appendix-title(body) = heading(level: 1)[#body]

#let pz-sig-line(label) = box(
  width: 5.5cm,
  stroke: (bottom: 0.5pt),
  inset: (bottom: 3pt),
)[#label]

// Без heading(level: 1): в gost перед ним всегда pagebreak (add-pagebreaks).
#let pz-front-heading(body, page-break: true) = {
  if page-break {
    pagebreak(weak: true)
  }
  align(center)[
    #text(weight: "bold")[#upper(body)]
  ]
  v(0.75em)
}

#let pz-biblio-strip(head, tail) = {
  table(
    columns: (0.82fr, 1fr),
    stroke: none,
    inset: (x: 0pt, y: 5pt),
    align: (left, left),
    [], head,
    [], tail,
  )
  v(0.65em)
}

#let pz-biblio-strip-ru(
  udk: "",
  author: "",
  title: "",
  direction: "09.03.04",
  institute: "Южный федеральный университет",
  faculty: "ИКТИБ",
  department: "кафедра математического обеспечения и применения ЭВМ",
  year: 2026,
) = {
  let pages = context counter(page).final().first()
  pz-biblio-strip(
    [
      УДК #udk
      #linebreak()
      #upper(author)
      #linebreak()
      #quote[#title]
    ],
    [
      Квалификационная работа на степень
      #linebreak()
      «БАКАЛАВР» по направлению #direction
      #linebreak()
      #institute,
      #linebreak()
      #faculty, #department – #year#sym.space.nobreak г.,
      #linebreak()
      #pages#sym.space.nobreak с.
    ],
  )
}

#let pz-biblio-strip-en(
  udk: "",
  author: "",
  title: "",
  direction: "09.03.04",
  institute: "Southern Federal University",
  faculty: "ICTIS",
  department: "the Department of Mathematical Support and Application of Computers (MOP EVM)",
  year: 2026,
) = {
  let pages = context counter(page).final().first()
  pz-biblio-strip(
    [
      UDC #udk
      #linebreak()
      #upper(author)
      #linebreak()
      #quote[#title]
    ],
    [
      Qualification work for the degree of
      #linebreak()
      BACHELOR in the direction of #direction
      #linebreak()
      #institute,
      #linebreak()
      #faculty, #department – #year,
      #linebreak()
      #pages#sym.space.nobreak p.
    ],
  )
}

#let pz-column-count(columns) = if type(columns) == int {
  columns
} else if type(columns) == array {
  columns.len()
} else {
  1
}

// Строка из ..range().map(i => ([a], [b])) в body.pos() – один аргумент-массив.
#let pz-flatten-cells(cells) = cells.fold((), (acc, cell) => {
  if type(cell) == array { acc + cell } else { acc + (cell,) }
})

#let pz-table-inner(columns, header-cells, tab-num, start-page, ..rows) = {
  let col-n = pz-column-count(columns)
  let cont-cell = table.cell(
    colspan: col-n,
    stroke: none,
    inset: (x: 0pt, y: 2pt),
    align: left,
  )[
    #context {
      if start-page.get() == none {
        start-page.update(here().page())
      }
      let first-page = start-page.get()
      if first-page != none and here().page() > first-page {
        [Продолжение таблицы #tab-num]
      }
    }
  ]
  let header-row = if header-cells.len() > 0 {
    (cont-cell, ..header-cells)
  } else {
    (cont-cell,)
  }
  table(
    columns: columns,
    table.header(..header-row, repeat: true),
    ..rows,
  )
}

#let pz-table(caption, columns, ..body) = {
  let pos = body.pos()
  let has-header = pos.len() > 0 and pos.first().func() == table.header
  let header-cells = if has-header { pos.first().children } else { () }
  let tail = pz-flatten-cells(if has-header { pos.slice(1) } else { pos })
  let start-page = state("pz-table-start-page", none)
  figure(
    kind: table,
    context {
      let fig-loc = here()
      let tab-num = counter(figure.where(kind: table)).at(fig-loc).first()
      start-page.update(none)
      pz-table-inner(columns, header-cells, tab-num, start-page, ..arguments(..tail))
    },
    caption: caption,
  )
}

// Реестры unit-тестов: перенос длинных идентификаторов (camelCase, _); сетка как в примере Typst.
#let pz-test-table(caption, columns, ..body) = {
  let pos = body.pos()
  let has-header = pos.len() > 0 and pos.first().func() == table.header
  let header-cells = if has-header { pos.first().children } else { () }
  let tail = pz-flatten-cells(if has-header { pos.slice(1) } else { pos })
  let start-page = state("pz-table-start-page", none)
  figure(
    kind: table,
    {
      show table: set text(hyphenate: true, size: 9pt)
      show table.cell: set block(inset: (x: 5pt, y: 4pt))
      show table.cell: cell => {
        show regex("[a-z0-9][A-Z]"): m => {
          m.text.first() + sym.zws + m.text.last()
        }
        show regex("[_]"): it => it + sym.zws
        cell
      }
      context {
        let fig-loc = here()
        let tab-num = counter(figure.where(kind: table)).at(fig-loc).first()
        start-page.update(none)
        pz-table-inner(columns, header-cells, tab-num, start-page, ..arguments(..tail))
      }
    },
    caption: caption,
  )
}

#let pz-fig(path, caption, lbl) = [
  #figure(
    image(
      "../images/" + path,
      width: 100%,
      fit: "contain",
    ),
    caption: caption,
  )
  #label(lbl)
]
