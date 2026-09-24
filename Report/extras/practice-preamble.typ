#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 1.5cm, top: 2cm, bottom: 2cm),
  numbering: none,
)
#set text(font: "Times New Roman", size: 14pt, lang: "ru")
#set par(justify: true, first-line-indent: 0pt)
#set table(stroke: 0.5pt + black, inset: (x: 6pt, y: 5pt))

#let practice_meta = (
  kind: "производственную",
  period: "ДД.ММ.ГГГГ – ДД.ММ.ГГГГ",
  org: "Организация",
  student: "Фамилия Имя Отчество",
  group: "группа",
  direction: "00.00.00 «Направление»",
  project: "название проекта",
)

#let practice_title(body) = {
  align(center)[
    #text(weight: "bold", size: 14pt)[#body]
  ]
  v(0.5em)
  align(center)[
    #practice_meta.student, группа #practice_meta.group \
    Направление #practice_meta.direction \
    #practice_meta.org \
    Сроки: #practice_meta.period \
    Проект: #practice_meta.project
  ]
  v(1em)
}
