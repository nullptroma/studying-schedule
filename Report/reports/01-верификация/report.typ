#import "@preview/modern-g7-32:0.2.0": gost
#import "meta.typ": meta
#import "../../includes/common.typ": pz-figure-caption-separator
#import "../../includes/pz-pagination.typ": pz_enable_pagination, pz_page_footer
#import "../../includes/title-page-prikladnaya-informatika.typ": pz-title-page

#set heading(numbering: "1.1.1.1")

// Титул «Прикладная информатика». Бланк МОП ЭВМ:
// #import "../../includes/title-page-mop-evm.typ": pz-title-page
// и поле department в meta.typ.
#show: gost.with(
  ministry: "Министерство науки и высшего образования Российской Федерации",
  organization: (
    full: "Федеральное государственное автономное образовательное учреждение высшего образования «Южный федеральный университет»",
    short: "ЮФУ",
  ),
  about: "отчёте",
  subject: meta.subject,
  city: meta.city,
  year: int(meta.year),
  performers: (
    (name: "Карев Д. В.", position: "студент"),
    (name: "Коновалов Д. Р.", position: "студент"),
  ),
  hide-title: true,
)

#set text(font: "Times New Roman")
#set page(footer: pz_page_footer)
#set figure.caption(separator: pz-figure-caption-separator)

#pz-title-page(meta)

#include "аннотация.typ"

#set outline(indent: 1.25cm / 2)
#outline()
#pagebreak(weak: true)
#pz_enable_pagination()

#include "обозначения.typ"
#include "введение.typ"
#include "верификация.typ"
#include "акторы.typ"
#include "заключение.typ"

#bibliography("источники.bib")
