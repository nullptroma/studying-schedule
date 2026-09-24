// Общие куски титульных бланков кафедр (подписи, оценка, шапка).
// Бланк кафедры: title-page-<кафедра>.typ (например title-page-mop-evm.typ).

#let pz-title-sig-width = 3.5cm

// Роли слева/справа (Пытков); линия по центру, одинаковой длины; под ней «подпись».
#let pz-title-sig-row(label, name, line-width: pz-title-sig-width) = {
  grid(
    columns: (1fr, line-width, 1fr),
    column-gutter: 10pt,
    row-gutter: 1pt,
    align: (left + bottom, center + bottom, right + bottom),
    label,
    box(
      width: 100%,
      height: 1em,
      stroke: (bottom: 0.6pt),
    )[],
    align(right)[#name],
    [],
    align(center)[#text(size: 8pt)[подпись]],
    [],
  )
}

#let pz-title-quote(body) = [«#body»]

#let pz-title-pair(top, bottom) = {
  stack(dir: ttb, spacing: 6pt, top, bottom)
}

// Блок оценки у правого края (как у Карманова).
#let pz-title-grade-block(year) = {
  set par(first-line-indent: 0pt, leading: 14pt, spacing: 0pt)
  align(right)[
    Оценка\
    #box(
      width: 5.5cm,
      stroke: (bottom: 0.6pt),
      inset: (bottom: 2pt),
    )[]\
    #v(8pt)
    «\_\_\_\_» \_\_\_\_\_\_\_\_\_\_\_\_\_ #year г.
  ]
}

// Шапка министерства / вуза / института / кафедры (ритм бланка ИКТИБ).
#let pz-title-header(
  ministry-short,
  university-quoted,
  institute,
  department,
) = {
  stack(
    dir: ttb,
    spacing: 11pt,
    ministry-short,
    text(size: 12pt)[
      #stack(
        dir: ttb,
        spacing: 5pt,
        [Федеральное государственное автономное образовательное учреждение высшего],
        [образования],
      )
    ],
    university-quoted,
    institute,
    department,
  )
}

// Тип работы / дисциплина / тема / вариант.
#let pz-title-work-block(work-type, discipline, topic, variant) = {
  stack(
    dir: ttb,
    spacing: 20pt,
    text(size: 22pt, weight: "bold")[#work-type],
    pz-title-pair(
      [по дисциплине],
      text(weight: "bold")[#pz-title-quote(discipline)],
    ),
    {
      let topic-block = pz-title-pair(
        [на тему:],
        text(weight: "bold")[#pz-title-quote(topic)],
      )
      if variant != none and variant != [] and variant != "" {
        stack(
          dir: ttb,
          spacing: 2pt,
          topic-block,
          text(style: "italic")[Вариант № #variant],
        )
      } else {
        topic-block
      }
    },
  )
}

// Выполнил / Принял (центрируется снаружи через v(1fr)).
#let pz-title-performers-block(
  student-name,
  student-position,
  reviewer-name,
  reviewer-position,
) = {
  pad(x: 0.4cm)[
    #set align(left)
    #set par(first-line-indent: 0pt, leading: 14pt, spacing: 0pt)
    #set block(spacing: 0pt)
    #stack(
      dir: ttb,
      spacing: 14pt,
      pz-title-pair(
        [Выполнил],
        pz-title-sig-row([#student-position], student-name),
      ),
      pz-title-pair(
        [Принял],
        pz-title-sig-row([#reviewer-position], reviewer-name),
      ),
    )
  ]
}
