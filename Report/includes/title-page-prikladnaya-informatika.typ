// Титульный бланк «Прикладная информатика» (ИКТИБ / ЮФУ).
// Близнец title-page-mop-evm.typ: та же раскладка, другой ряд логотипов.
// Поля отчёта приходят словарём meta из каталога этого отчёта.
#import "title-page-common.typ": (
  pz-title-grade-block,
  pz-title-header,
  pz-title-pair,
  pz-title-performers-block,
  pz-title-sig-row,
  pz-title-work-block,
)

#let pz-logo-sfedu = "../images/logos/sfedu.png"
#let pz-logo-iktib = "../images/logos/iktib.png"

// Ряд логотипов: только ЮФУ + ИКТИБ (отдельного знака кафедры нет).
#let pz-title-logos-prikladnaya-informatika(
  sfedu: pz-logo-sfedu,
  iktib: pz-logo-iktib,
  height: 4cm,
) = {
  grid(
    columns: (auto, auto),
    column-gutter: 1.4cm,
    align: (center + horizon, center + horizon),
    image(sfedu, height: height),
    image(iktib, height: height),
  )
}

#let pz-title-page(meta) = {
  let ministry-short = meta.at("ministry-short", default: "МИНОБРНАУКИ РОССИИ")
  let university-quoted = meta.at("university-quoted", default: "«ЮЖНЫЙ ФЕДЕРАЛЬНЫЙ УНИВЕРСИТЕТ»")
  let institute = meta.at("institute", default: "Институт компьютерных технологий и информационной безопасности")
  let department = meta.department
  let work-type = meta.at("work-type", default: "ОТЧЁТ")
  let discipline = meta.discipline
  let topic = meta.topic
  let variant = meta.at("variant", default: "")
  let student-name = meta.student-name
  let student-position = meta.student-position
  let reviewer-name = meta.reviewer-name
  let reviewer-position = meta.reviewer-position
  let city = meta.city
  let year = meta.year
  let show-logos = meta.at("show-logos", default: true)
  // Поля бланка ИКТИБ (DOCX pgMar: top/bottom 1.5 cm, left/right 2 cm).
  page(
    margin: (top: 1.5cm, bottom: 1.5cm, left: 2cm, right: 2cm),
    {
      set text(font: "Times New Roman", size: 14pt)
      set par(first-line-indent: 0pt, justify: false, leading: 14pt, spacing: 0pt)
      set block(spacing: 0pt)
      set align(center)

      pz-title-header(ministry-short, university-quoted, institute, department)

      if show-logos {
        v(12pt)
        pz-title-logos-prikladnaya-informatika()
        v(22pt)
      } else {
        v(28pt)
      }

      pz-title-work-block(work-type, discipline, topic, variant)

      // Исполнители на этом бланке, без отдельного листа пакета gost.
      let students = meta.at("students", default: none)
      v(1fr)
      if type(students) == array and students.len() > 0 {
        pad(x: 0.4cm)[
          #set align(left)
          #set par(first-line-indent: 0pt, leading: 14pt, spacing: 0pt)
          #set block(spacing: 0pt)
          #stack(
            dir: ttb,
            spacing: 22pt,
            pz-title-pair(
              [Выполнил],
              stack(
                dir: ttb,
                spacing: 8pt,
                ..students.map(person => pz-title-sig-row(
                  [#person.position],
                  person.name,
                )),
              ),
            ),
            pz-title-pair(
              [Принял],
              pz-title-sig-row([#reviewer-position], reviewer-name),
            ),
          )
        ]
      } else {
        pz-title-performers-block(
          student-name,
          student-position,
          reviewer-name,
          reviewer-position,
        )
      }
      v(1fr)

      // Оценка – отдельно у низа, над «Таганрог».
      pad(x: 0.4cm)[
        #pz-title-grade-block(year)
      ]
      v(0.85cm)
      align(center)[#city #year]
    },
  )
}
