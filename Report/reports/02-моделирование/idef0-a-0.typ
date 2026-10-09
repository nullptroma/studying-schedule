// Собран скриптом скрипты/собрать-отчёт-02.py.
#import "../../includes/common.typ": pz-table
#import "../../includes/pz-pagination.typ": pz_page_footer

= Контекстная диаграмма IDEF0 A-0

Функция системы – управлять учебным расписанием. Буква задаёт роль дуги: I – вход, C – управление, O – выход, M – механизм. Цвет повторяет роль: голубой – вход и выход, красный – жёсткое управление, персиковый – мягкий критерий, розовый – механизм, зелёный – функция.

Диаграмма приведена на #ref(<fig-idef0-a-0>, supplement: [рисунке]).

#set page(flipped: true, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
#figure(
  image(
    "../../images/fig_02_idef0_a0_ctx.png",
    width: 100%,
    height: 14.8cm,
    fit: "contain",
  ),
  caption: [Контекстная диаграмма IDEF0 A-0 информационной системы управления учебным расписанием],
) <fig-idef0-a-0>
#set page(flipped: false, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
