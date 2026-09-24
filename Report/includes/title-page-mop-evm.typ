// Титульный бланк кафедры МОП ЭВМ (ИКТИБ / ЮФУ).
// Соседний бланк другой кафедры: скопировать этот файл → title-page-<кафедра>.typ
// и подставить свой ряд логотипов. Название кафедры берётся из meta отчёта.
#import "title-page-common.typ": (
  pz-title-grade-block,
  pz-title-header,
  pz-title-performers-block,
  pz-title-work-block,
)

#let pz-logo-sfedu = "../images/logos/sfedu.png"
#let pz-logo-iktib = "../images/logos/iktib.png"
#let pz-logo-mop = "../images/logos/mop-evm.png"

// Ряд логотипов МОП ЭВМ: ЮФУ + ИКТИБ + МОП ЭВМ (как на бланке Карманова).
#let pz-title-logos-mop-evm(
  sfedu: pz-logo-sfedu,
  iktib: pz-logo-iktib,
  mop: pz-logo-mop,
  height: 4cm,
) = {
  grid(
    columns: (auto, auto, auto),
    column-gutter: 0.85cm,
    align: (center + horizon, center + horizon, center + horizon),
    image(sfedu, height: height),
    image(iktib, height: height),
    image(mop, height: height),
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
        pz-title-logos-mop-evm()
        v(22pt)
      } else {
        v(28pt)
      }

      pz-title-work-block(work-type, discipline, topic, variant)

      // Выполнил/Принял – по центру между темой и блоком оценки.
      v(1fr)
      pz-title-performers-block(
        student-name,
        student-position,
        reviewer-name,
        reviewer-position,
      )
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
