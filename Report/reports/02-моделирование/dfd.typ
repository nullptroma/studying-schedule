// Собран скриптом скрипты/собрать-отчёт-02.py.
#import "../../includes/common.typ": pz-table
#import "../../includes/pz-pagination.typ": pz_page_footer

= DFD уровня 0

Студент, преподаватель и администратор находятся вне системы. Процессы 1.0–5.0 и хранилища D1–D6 относятся к системе. Одобренное изменение возвращается из процесса 5.0 в процесс 2.0.

Диаграмма приведена на #ref(<fig-dfd-0>, supplement: [рисунке]).

#set page(flipped: true, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
#figure(
  image(
    "../../images/fig_02_dfd_0.png",
    width: 100%,
    height: 14.8cm,
    fit: "contain",
  ),
  caption: [DFD-диаграмма потоков данных информационной системы управления учебным расписанием],
) <fig-dfd-0>
#set page(flipped: false, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
