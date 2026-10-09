---
тип: модель
порядок: 3
рисунок: fig_02_idef0_a0
подпись: Декомпозиция IDEF0 A0 процесса управления учебным расписанием
метка: fig-idef0-a0
файл: idef0-a0.typ
tags:
  - модель
  - отчёт-2
---

# Декомпозиция IDEF0 A0

A1 готовит данные, A2 отбирает допустимые варианты, A3 оптимизирует, A4 публикует, A5 обрабатывает заявку. Одобренное изменение возвращается в A2.

Жёсткие ограничения: нет двойной занятости преподавателя, группы и аудитории, аудитория подходит занятию. Мягкие критерии: меньше окон, ровнее нагрузка, рациональнее аудиторный фонд.

## Диаграмма

```plantuml
@startuml
skinparam linetype ortho
skinparam nodesep 30
skinparam ranksep 40
skinparam defaultTextAlignment center

rectangle "C1\nЖёсткие\nограничения" as C1 #F4CCCC
rectangle "C2\nМягкие\nкритерии" as C2 #FCE5CD
rectangle "C3\nКалендарь\nи регламенты" as C3 #F4CCCC

rectangle "A1\nПодготовить\nисходные данные" as A1 #D9EAD3
rectangle "A2\nСформировать\nдопустимые\nварианты" as A2 #D9EAD3
rectangle "A3\nОптимизировать\nрасписание" as A3 #D9EAD3
rectangle "A4\nПроверить\nи опубликовать" as A4 #D9EAD3
rectangle "A5\nОбработать\nзаявку" as A5 #D9EAD3

rectangle "I1\nУчебная\nнагрузка" as I1 #D9EAF7
rectangle "I2\nАудиторный\nфонд" as I2 #D9EAF7
rectangle "I3\nЗаявки на\nизменение" as I3 #D9EAF7

rectangle "O1\nОпубликованное\nрасписание" as O1 #D9EAF7
rectangle "O3\nОтчёт о\nконфликтах" as O3 #D9EAF7
rectangle "O2\nРешение\nпо заявке" as O2 #D9EAF7

C1 -[hidden]right- C2
C2 -[hidden]right- C3
A1 -[hidden]right- A2
A2 -[hidden]right- A3
A3 -[hidden]right- A4
A1 -[hidden]down- A5
I1 -[hidden]right- I2
I2 -[hidden]right- I3
O1 -[hidden]right- O3
O3 -[hidden]right- O2

C1 -[hidden]down- A1
A1 -[hidden]down- I1
A4 -[hidden]down- O1
A5 -[hidden]right- O2

C1 -down-> A2
C1 -down-> A4
C1 -down-> A5
C2 -down-> A3
C3 -down-> A1
C3 -down-> A4

I1 -up-> A1
I2 -up-> A1
I3 -up-> A5

A1 -right-> A2 : данные
A2 -right-> A3 : варианты
A3 -right-> A4 : оптимум
A4 -down-> O1
A4 -down-> O3
A4 -down-> A5 : расписание
A5 -left-> A2 : изменение
A5 -down-> O2
@enduml
```
