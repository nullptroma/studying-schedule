// Собран скриптом скрипты/собрать-отчёт-01.py из заметок акторов.
#set page(
  flipped: true,
  margin: (left: 15mm, right: 15mm, top: 14mm, bottom: 14mm),
)

= Лист акторов и их действия

Рабочая точка – уникальное подлежащее после перевода требования в активный залог. Веб-сайт и система здесь обозначают саму проектируемую систему.

#[
  #set text(size: 9pt)
  #set par(justify: false, first-line-indent: (amount: 0pt, all: true), leading: 0.65em, spacing: 0.4em)
  #table(
    columns: (3707fr, 11431fr),
    stroke: 0.5pt,
    inset: 4pt,
    align: left + top,
    table.header(
      repeat: true,
      table.cell(fill: rgb("#E2F0D9"), align: left + top)[#text(weight: "bold")[Актер]],
      table.cell(fill: rgb("#E2F0D9"), align: left + top)[#text(weight: "bold")[Действия]],
    ),
    table.cell(align: left + top, breakable: false)[Веб-сайт], table.cell(align: left + top, breakable: false)[• адаптирует компоновку всех страниц к заданным диапазонам ширины области просмотра – REQ-001 \
• обеспечивает доступность пользовательских функций и корректное отображение интерфейса на поддерживаемых ОС – REQ-002 \
• отображает интерфейс и предоставляет пользовательские функции в поддерживаемых браузерах – REQ-003 \
• использует заданные технологии клиентской части и обеспечивает корректность HTML-разметки – REQ-004 \
• формирует и возвращает страницу расписания в заданное время отклика – REQ-005 \
• получает требуемые оценки Google Lighthouse – REQ-006 \
• обслуживает заданное число одновременных пользователей с установленным уровнем ошибок – REQ-007],
    table.cell(align: left + top, breakable: false)[Пользователь], table.cell(align: left + top, breakable: false)[• выбирает русский или английский язык интерфейса – REQ-008 \
• получает расписание выбранной учебной группы на выбранную дату – REQ-009 \
• просматривает сведения об учебных корпусах, аудиториях и контактах администрации – REQ-010],
    table.cell(align: left + top, breakable: false)[Пользователь с ролью «Администратор»], table.cell(align: left + top, breakable: false)[• добавляет информацию о расписании – REQ-011 \
• редактирует информацию о расписании – REQ-011],
    table.cell(align: left + top, breakable: false)[Заказчик], table.cell(align: left + top, breakable: false)[• устанавливает сайт сервиса на своей площадке – REQ-014],
    table.cell(align: left + top, breakable: false)[Система], table.cell(align: left + top, breakable: false)[• предоставляет актуальное расписание занятий университетам, школам, в том числе онлайн-школам, и колледжам – REQ-013 \
• передаёт данные между клиентом и сервером по HTTPS с TLS 1.2 или новее – REQ-012 \
• перенаправляет обращения по HTTP на HTTPS – REQ-012],
  )
]
