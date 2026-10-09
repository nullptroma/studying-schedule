// Собран скриптом скрипты/собрать-отчёт-02.py.
#import "../../includes/common.typ": pz-table
#import "../../includes/pz-pagination.typ": pz_page_footer

= Декомпозиция IDEF0 A0

A1 готовит данные, A2 отбирает допустимые варианты, A3 оптимизирует, A4 публикует, A5 обрабатывает заявку. Одобренное изменение возвращается в A2.

Жёсткие ограничения: нет двойной занятости преподавателя, группы и аудитории, аудитория подходит занятию. Мягкие критерии: меньше окон, ровнее нагрузка, рациональнее аудиторный фонд.

Диаграмма приведена на #ref(<fig-idef0-a0>, supplement: [рисунке]).

#set page(flipped: true, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
#figure(
  image(
    "../../images/fig_02_idef0_a0.png",
    width: 100%,
    height: 14.8cm,
    fit: "contain",
  ),
  caption: [Декомпозиция IDEF0 A0 процесса управления учебным расписанием],
) <fig-idef0-a0>
#set page(flipped: false, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)
