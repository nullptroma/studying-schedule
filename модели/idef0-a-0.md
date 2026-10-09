---
тип: модель
порядок: 2
рисунок: fig_02_idef0_a0_ctx
подпись: Контекстная диаграмма IDEF0 A-0 информационной системы управления учебным расписанием
метка: fig-idef0-a-0
файл: idef0-a-0.typ
tags:
  - модель
  - отчёт-2
---

# Контекстная диаграмма IDEF0 A-0

Функция системы — управлять учебным расписанием. Буква задаёт роль дуги: I — вход, C — управление, O — выход, M — механизм. Цвет повторяет роль: голубой — вход и выход, красный — жёсткое управление, персиковый — мягкий критерий, розовый — механизм, зелёный — функция.

## Диаграмма

```plantuml
@startuml
skinparam linetype ortho
skinparam nodesep 24
skinparam ranksep 28
skinparam defaultTextAlignment center

rectangle "C1\nЖёсткие\nограничения" as C1 #F4CCCC
rectangle "C2\nМягкие\nкритерии" as C2 #FCE5CD
rectangle "C3\nКалендарь\nи регламенты" as C3 #F4CCCC

rectangle "I1\nУчебная\nнагрузка" as I1 #D9EAF7
rectangle "I2\nДоступность" as I2 #D9EAF7
rectangle "I3\nЗаявки" as I3 #D9EAF7

rectangle "A-0\nУправлять\nучебным\nрасписанием" as A0 #D9EAD3

rectangle "O1\nОпубликованное\nрасписание" as O1 #D9EAF7
rectangle "O2\nРешение\nпо заявке" as O2 #D9EAF7
rectangle "O3\nОтчёт\nо конфликтах" as O3 #D9EAF7

rectangle "M1\nАдминистратор" as M1 #EAD1DC
rectangle "M2\nБаза данных" as M2 #EAD1DC
rectangle "M3\nМодуль\nформирования" as M3 #EAD1DC

C1 -[hidden]right- C2
C2 -[hidden]right- C3
I1 -[hidden]down- I2
I2 -[hidden]down- I3
O1 -[hidden]down- O2
O2 -[hidden]down- O3
M1 -[hidden]right- M2
M2 -[hidden]right- M3

C2 -[hidden]down- A0
I2 -[hidden]right- A0
A0 -[hidden]right- O2
A0 -[hidden]down- M2

C1 -down-> A0
C2 -down-> A0
C3 -down-> A0
I1 -right-> A0
I2 -right-> A0
I3 -right-> A0
A0 -right-> O1
A0 -right-> O2
A0 -right-> O3
M1 -up-> A0
M2 -up-> A0
M3 -up-> A0
@enduml
```
