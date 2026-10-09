// Собран скриптом скрипты/собрать-отчёт-02.py.
#import "../../includes/common.typ": pz-table
#import "../../includes/pz-pagination.typ": pz_page_footer

= Информационная модель IDEF1

Сущности, атрибуты и связи предметной области. Пунктир – необязательная ссылка заявки на запись расписания, интервал или аудиторию.

Диаграмма приведена на #ref(<fig-idef1>, supplement: [рисунке]).

#set page(flipped: true, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
#figure(
  image(
    "../../images/fig_02_idef1.png",
    width: 100%,
    height: 14.8cm,
    fit: "contain",
  ),
  caption: [Информационная модель IDEF1 системы управления учебным расписанием],
) <fig-idef1>
#set page(flipped: false, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
