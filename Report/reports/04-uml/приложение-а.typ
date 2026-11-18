// Собран скриптом скрипты/собрать-отчёт-04.py.

#import "../../includes/common.typ": pz-appendix-title

#pz-appendix-title[Исходные тексты диаграмм PlantUML]

#show raw: set text(font: "DejaVu Sans Mono", size: 8pt)
#set par(first-line-indent: 0pt)

Каждый листинг – содержимое блока plantuml в заметке диаграммы. При сборке скрипт добавляет к нему тему оформления по ГОСТ и выгружает в каталог Report/puml.

#block(breakable: false, below: 0.4em)[Листинг А.1 – Диаграмма прецедентов ИС «Учебное расписание»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
left to right direction
skinparam nodesep 14
skinparam ranksep 40

actor \"Администратор\" as Admin
actor \"Преподаватель\" as Teacher
actor \"Студент\" as Student
actor \"Внешняя учебная ИС\" as External

rectangle \"ИС «Учебное расписание»\" {
  usecase \"UC-01 Вести справочники\\nи учебную нагрузку\" as UC01 #D9EAD3
  usecase \"UC-02 Задать ограничения\\nи доступность\" as UC02 #D9EAD3
  usecase \"UC-03 Сформировать\\nпроект расписания\" as UC03 #FCE5CD
  usecase \"UC-04 Проверить\\nограничения\" as UC04 #FFF2CC
  usecase \"UC-05 Сократить окна\" as UC05 #FFF2CC
  usecase \"UC-06 Перенести\\nзанятие\" as UC06 #FCE5CD
  usecase \"UC-07 Получить варианты\\nустранения конфликта\" as UC07 #FFF2CC
  usecase \"UC-08 Утвердить и\\nопубликовать версию\" as UC08 #FCE5CD
  usecase \"UC-09 Просмотреть\\nрасписание группы\" as UC09 #D9EAF7
  usecase \"UC-10 Просмотреть\\nсправочные сведения\" as UC10 #D9EAF7
  usecase \"UC-11 Экспортировать\\nрасписание\" as UC11 #D9EAF7
  usecase \"UC-12 Сравнить версии\\nрасписания\" as UC12 #D9EAD3
  usecase \"UC-13 Отменить\\nгенерацию\" as UC13 #FFF2CC
}

Admin --> UC01
Admin --> UC02
Admin --> UC03
Admin --> UC06
Admin --> UC08
Admin --> UC12
Teacher --> UC02 : доступность
Teacher --> UC09
Teacher --> UC10
Student --> UC09
Student --> UC10
UC11 <-- External

UC03 ..> UC04 : <<include>>
UC03 ..> UC05 : <<include>>
UC06 ..> UC04 : <<include>>
UC08 ..> UC04 : <<include>>
UC07 ..> UC06 : <<extend>>
UC13 ..> UC03 : <<extend>>
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.2 – Диаграмма классов ИС «Учебное расписание»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
skinparam linetype ortho
skinparam nodesep 40
skinparam ranksep 50
skinparam classAttributeIconSize 0
hide circle

abstract class User <<entity>> #D9EAD3 {
  -id : UUID
  -fullName : String
  -email : String
  -role : String
  +hasPermission(action : String) : Boolean
}
class Administrator <<entity>> #D9EAD3 {
  -position : String
}
class Teacher <<entity>> #D9EAD3 {
  -department : String
  -availability : Set<TimeSlot>
  +isAvailable(slot : TimeSlot) : Boolean
}
class StudentGroup <<entity>> #D9EAD3 {
  -id : UUID
  -name : String
  -faculty : String
  -studentCount : Integer
}
class Classroom <<entity>> #D9EAD3 {
  -id : UUID
  -number : String
  -capacity : Integer
  -roomType : String
  -buildingName : String
  -buildingAddress : String
  +fits(assignment : TeachingAssignment) : Boolean
}
class TeachingAssignment <<entity>> #D9EAD3 {
  -id : UUID
  -courseName : String
  -lessonType : String
  -requiredHours : Integer
  -requiredRoomType : String
  +getRemainingHours(version : ScheduleVersion) : Integer
}
class TimeSlot <<entity>> #D9EAD3 {
  -id : UUID
  -weekday : Integer
  -periodNumber : Integer
  -startsAt : Time
  -endsAt : Time
}
class Lesson <<entity>> #D9EAD3 {
  -id : UUID
  -weekPattern : String
  +reschedule(slot : TimeSlot, room : Classroom) : Void
}
class ScheduleVersion <<entity>> #D9EAD3 {
  -id : UUID
  -semester : String
  -status : String
  -createdAt : DateTime
  -publishedAt : DateTime
  -gapsScore : Integer
  +addLesson(lesson : Lesson) : Void
  +updateLesson(lessonId : UUID, slotId : UUID, roomId : UUID) : Void
  +setStatus(status : String) : Void
  +cloneAsDraft() : ScheduleVersion
}
class ScheduleUI <<boundary>> #D9EAF7 {
  -language : String
  +requestGeneration(params : Map) : Void
  +cancelGeneration(versionId : UUID) : Void
  +requestMove(lessonId : UUID, slotId : UUID, roomId : UUID) : Void
  +requestPublish(versionId : UUID) : Void
  +showSchedule(versionId : UUID) : Void
  +showGroupSchedule(groupId : UUID, date : Date) : Void
  +showConflicts(conflicts : List) : Void
  +projectReady(version : ScheduleVersion) : Void
  +generationFailed(conflicts : List) : Void
  +moveAccepted(gapsScore : Integer) : Void
  +moveRejected(conflicts : List) : Void
  +published(version : ScheduleVersion) : Void
  +publishRejected(reasons : List) : Void
}
class ScheduleService <<control>> #FCE5CD {
  +generateDraft(params : Map) : ScheduleVersion
  +cancelGeneration(versionId : UUID) : Void
  +moveLesson(lessonId : UUID, slotId : UUID, roomId : UUID) : List
  +checkVersion(versionId : UUID) : List
  +publishVersion(versionId : UUID) : Boolean
}
class ConstraintChecker <<service>> #FFF2CC {
  +validateLesson(lesson : Lesson, version : ScheduleVersion) : List
  +validateVersion(version : ScheduleVersion) : List
  +validateRequiredHours(version : ScheduleVersion) : Boolean
  +calculateGaps(version : ScheduleVersion) : Integer
}

User <|-- Administrator
User <|-- Teacher

ScheduleUI ..> ScheduleService : вызывает >
ScheduleService ..> ScheduleVersion : создаёт >
ScheduleService ..> ConstraintChecker : проверяет >

Administrator \"1\" -- \"0..*\" ScheduleVersion : публикует >
Teacher \"1\" -- \"0..*\" TeachingAssignment : ведёт >
StudentGroup \"1..*\" -- \"0..*\" TeachingAssignment : получает >
ScheduleVersion \"1\" *-- \"0..*\" Lesson : содержит >
TeachingAssignment \"1\" -- \"0..*\" Lesson : реализуется >
TimeSlot \"1\" -- \"0..*\" Lesson : назначен >
Classroom \"1\" -- \"0..*\" Lesson : размещает >

ConstraintChecker ..> Lesson : анализирует >
ConstraintChecker ..> Teacher : доступность >
ConstraintChecker ..> Classroom : вместимость >
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.3 – Диаграмма последовательности UC-03 «Сформировать проект расписания»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
skinparam sequenceMessageAlign center
skinparam maxMessageSize 220

actor \"Администратор\" as D
boundary \"ui:ScheduleUI\" as UI #D9EAF7
control \"service:ScheduleService\" as S #FCE5CD
control \"checker:ConstraintChecker\" as C #FFF2CC
entity \"version:ScheduleVersion\" as V #D9EAD3
entity \"assignment:TeachingAssignment\" as A #D9EAD3

D -> UI : requestGeneration(params)
UI ->> S : generateDraft(params)
activate S
UI --> D : статус «Генерация»
create V
S -> V : <<create>> status = «Генерация»

loop для каждого учебного назначения
  break получен cancelGeneration(versionId)
    D -> UI : cancelGeneration(versionId)
    UI -> S : cancelGeneration(versionId)
    S -> V : setStatus(«Отменено»)
    S -->> UI : generationFailed([«отменено»])
  end
  S -> A : getRemainingHours(version)
  A --> S : hours
  loop пока hours > 0 и есть слоты
    S -> C : validateLesson(candidate, version)
    C --> S : conflicts
    alt conflicts пуст
      S -> V : addLesson(candidate)
    else есть нарушения
      note right of C : О-04…О-06: кандидат отвергается
    end
  end
end

S -> V : setStatus(«Проверка»)
S -> C : validateVersion(version)
C --> S : conflicts
S -> C : validateRequiredHours(version)
C --> S : covered

alt конфликтов нет и нагрузка покрыта
  S -> C : calculateGaps(version)
  C --> S : gapsScore
  S -> V : setStatus(«Готово»)
  S -->> UI : projectReady(version)
  UI -> UI : showSchedule(versionId)
  UI --> D : проект расписания
else решение не найдено
  S -> V : setStatus(«Ошибка»)
  S -->> UI : generationFailed(conflicts)
  UI -> UI : showConflicts(conflicts)
  UI --> D : причины и непокрытые часы
end
deactivate S

note over S, V : БТ-02, БТ-03, ПТ-03, ПТ-04, СХ-05
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.4 – Диаграмма последовательности UC-06 «Перенести занятие»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
skinparam sequenceMessageAlign center
skinparam maxMessageSize 220

actor \"Администратор\" as D
boundary \"ui:ScheduleUI\" as UI #D9EAF7
control \"service:ScheduleService\" as S #FCE5CD
control \"checker:ConstraintChecker\" as C #FFF2CC
entity \"version:ScheduleVersion\" as V #D9EAD3
entity \"lesson:Lesson\" as L #D9EAD3
entity \"teacher:Teacher\" as T #D9EAD3
entity \"room:Classroom\" as R #D9EAD3

D -> UI : requestMove(lessonId, slotId, roomId)
UI -> S : moveLesson(lessonId, slotId, roomId)
activate S
opt версия в статусе «Опубликовано»
  S -> V : cloneAsDraft()
  V --> S : draft
  note right of S : О-07: правится только черновик
end

S -> C : validateLesson(candidate, version)
activate C
C -> T : isAvailable(slot)
T --> C : available
C -> R : fits(assignment)
R --> C : fits
C --> S : conflicts
deactivate C

alt кандидат допустим
  S -> V : updateLesson(lessonId, slotId, roomId)
  V -> L : reschedule(slot, room)
  S -> V : setStatus(«Проверка»)
  S -> C : validateVersion(version)
  C --> S : conflicts
  alt версия без нарушений
    S -> C : calculateGaps(version)
    C --> S : gapsScore
    S -> V : setStatus(«Готово»)
    S --> UI : moveAccepted(gapsScore)
    UI -> UI : showSchedule(versionId)
  else найдены иные нарушения
    V -> L : reschedule(prevSlot, prevRoom)
    S -> V : setStatus(«Черновик»)
    S --> UI : moveRejected(conflicts)
    UI -> UI : showConflicts(conflicts)
  end
else слот занят или аудитория не подходит
  S --> UI : moveRejected(conflicts)
  UI -> UI : showConflicts(conflicts)
  note right of UI : UC-07: варианты устранения конфликта
end
deactivate S
UI --> D : результат переноса

note over C, R : ПТ-05, О-04…О-06, КП-04
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.5 – Диаграмма последовательности UC-08 «Утвердить и опубликовать версию»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
skinparam sequenceMessageAlign center
skinparam maxMessageSize 220

actor \"Администратор\" as D
actor \"Студент\" as St
boundary \"ui:ScheduleUI\" as UI #D9EAF7
control \"service:ScheduleService\" as S #FCE5CD
entity \"admin:Administrator\" as Adm #D9EAD3
control \"checker:ConstraintChecker\" as C #FFF2CC
entity \"version:ScheduleVersion\" as V #D9EAD3
entity \"current:ScheduleVersion\" as P #D9EAD3

D -> UI : requestPublish(versionId)
UI -> S : publishVersion(versionId)
activate S
S -> Adm : hasPermission(«publish»)
Adm --> S : allowed

alt allowed = false
  S --> UI : publishRejected([«нет прав»])
else права подтверждены
  S -> S : checkVersion(versionId)
  activate S
  S -> C : validateVersion(version)
  C --> S : conflicts
  S -> C : validateRequiredHours(version)
  C --> S : covered
  deactivate S
  alt конфликтов нет и нагрузка покрыта
    group транзакция
      S -> P : setStatus(«Архив»)
      S -> V : setStatus(«Опубликовано»)
    end
    S --> UI : published(version)
    UI -> UI : showSchedule(versionId)
  else есть конфликт или непокрытые часы
    S --> UI : publishRejected(conflicts)
    UI -> UI : showConflicts(conflicts)
  end
end
deactivate S
UI --> D : итог публикации

opt после публикации
  St -> UI : showGroupSchedule(groupId, date)
  UI --> St : расписание группы на дату
end

note over S, P : ПТ-06, О-01, О-07, КП-05
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.6 – Диаграмма деятельности «Формирование и публикация расписания»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
|Администратор|
start
:Ввести период и веса критериев;
|ScheduleUI|
:requestGeneration(params);
|ScheduleService|
:generateDraft(params);
fork
  :Загрузить учебные назначения
  и доступность преподавателей;
fork again
  :Загрузить группы, аудитории
  и временные слоты;
end fork
:Разместить занятия
по жёстким ограничениям;
:Сократить окна
преподавателей и групп;
|ConstraintChecker|
:validateVersion(version);
:validateRequiredHours(version);
|Администратор|
:Расчёт завершён; <<acceptEvent>>
|ScheduleService|
if (Есть нарушения или\\nнепокрытые часы?) then (да)
  :Статус «Ошибка»;
  |ScheduleUI|
  :showConflicts(conflicts);
  |Администратор|
  :Исправить исходные данные;
  stop
else (нет)
  |ScheduleService|
  :Статус «Готово»;
endif
|ScheduleUI|
:showSchedule(versionId);
|Администратор|
if (Нужна правка?) then (да)
  :Перенести занятие (UC-06);
  |ScheduleService|
  :moveLesson(lessonId, slotId, roomId);
  |ConstraintChecker|
  :validateVersion(version);
  if (Перенос допустим?) then (нет)
    |ScheduleService|
    :Откатить перенос;
    |ScheduleUI|
    :showConflicts(conflicts);
  else (да)
  endif
else (нет)
endif
|Администратор|
:Подтвердить проект;
|ScheduleUI|
:requestPublish(versionId);
|ScheduleService|
:publishVersion(versionId);
if (Версия корректна\\nи права есть?) then (да)
  :Архивировать прежнюю версию,
  опубликовать новую;
  |ScheduleUI|
  :Открыть опубликованное расписание;
else (нет)
  |ScheduleUI|
  :publishRejected(reasons);
endif
stop
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.7 – Диаграмма состояний класса ScheduleVersion]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
hide empty description

state \"Черновик\" as Draft #D9EAF7
state \"Генерация\" as Generating #FFF2CC
state \"Проверка\" as Checking #FFF2CC
state \"Готово\" as Ready #D9EAD3
state \"Опубликовано\" as Published #D9EAD3
state \"Архив\" as Archived
state \"Ошибка\" as Error #F4CCCC
state \"Отменено\" as Canceled #F4CCCC

[*] --> Draft : создать версию / save
Draft --> Generating : generateDraft() [данные заданы] / запуск расчёта
Generating --> Checking : вариант построен / validateVersion()
Generating --> Error : [занятия не размещены] / отчёт о причинах
Generating --> Canceled : cancelGeneration() / прервать расчёт
Checking --> Ready : [нет конфликтов, нагрузка покрыта] / calculateGaps()
Checking --> Error : [есть конфликты] / showConflicts()
Error --> Draft : исправить данные / повторить
Ready --> Checking : moveLesson() / validateVersion()
Ready --> Published : publishVersion() [права и проверка] / publish
Ready --> Canceled : отменить проект
Draft --> Canceled : отменить проект
Published --> Draft : cloneAsDraft() / новая версия
Published --> Archived : опубликована новая версия / archive
Archived --> [*]
Canceled --> [*]
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.8 – Диаграмма компонентов ИС «Учебное расписание»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
skinparam componentStyle uml2
skinparam nodesep 35
skinparam ranksep 45

package \"Клиент\" #EEF5FC {
  component \"Веб-интерфейс\\n[ScheduleUI]\" as UI #D9EAF7
}

package \"Сервер приложения\" #FFF8EE {
  interface \"IPlanningApi\" as IPlan
  component \"API и контроль доступа\\n[User, Administrator, Teacher]\" as Access #FCE5CD
  component \"Планировщик\\n[ScheduleService]\" as Solver #FCE5CD
  interface \"ICatalog\" as ICat
  interface \"IConstraints\" as ICons
  interface \"IScheduleStore\" as IStore
  component \"Каталог ресурсов\\n[StudentGroup, Classroom,\\nTeachingAssignment, TimeSlot]\" as Catalog #D9EAD3
  component \"Проверка ограничений\\n[ConstraintChecker]\" as Checker #FFF2CC
  component \"Хранилище версий\\n[ScheduleVersion, Lesson]\" as Storage #D9EAD3
  component \"Экспорт\" as Export #D9EAF7
  interface \"IExport\" as IExp
  note \"БТ-02, БТ-03: сначала жёсткие\\nограничения, затем окна\" as NSolver
  note \"О-01: правка только\\nадминистратору\" as NAccess
}

component \"Внешняя учебная ИС\" as Ext <<external>>

UI -down-( IPlan : HTTPS / REST
IPlan -down- Access
Access -down-( ICat
Access -right-> Solver : запуск расчёта
Solver -down-( ICons
Solver -down-( IStore
ICat -down- Catalog
ICons -down- Checker
Checker -left-( ICat
IStore -down- Storage
Export -up-( IStore
Export -down- IExp
Ext -up-( IExp
NSolver .up. Solver
NAccess .left. Access

note right of UI : СХ-01…СХ-04, ПТ-09
@enduml
"))

#block(breakable: false, below: 0.4em)[Листинг А.9 – Диаграмма развёртывания ИС «Учебное расписание»]
#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "@startuml
left to right direction
skinparam nodesep 30
skinparam ranksep 70

node \"Устройство пользователя\\nWindows 10/11, macOS 13+,\\nAndroid 12+, iOS 16+\" as Client <<device>> #EEF5FC {
  artifact \"Браузер: Chrome, Edge,\\nFirefox, Safari\\n[Веб-интерфейс]\" as Browser #D9EAF7
}

node \"Площадка заказчика\" as Site <<self-host>> #FFF8EE {
  node \"Сервер приложения\" as App <<executionEnvironment>> #FFFFFF {
    artifact \"API и контроль доступа\" as API #FCE5CD
    artifact \"Планировщик\" as Solver #FCE5CD
    artifact \"Проверка ограничений\" as Checker #FFF2CC
    artifact \"Каталог ресурсов\" as Catalog #D9EAD3
    artifact \"Экспорт\" as Export #D9EAF7
  }
  node \"Сервер БД\" as Db <<database>> #FFFFFF {
    database \"Реляционная БД:\\nсправочники, версии,\\nзанятия\" as SQL #D9EAD3
  }
}

node \"Внешняя учебная ИС\" as Ext <<external>>

Browser --> API : HTTPS, TLS 1.2+\\nHTTP → HTTPS
API --> Solver : внутренний вызов
Solver --> Checker : внутренний вызов
API --> SQL : SQL / TCP, TLS
Catalog --> SQL : SQL / TCP, TLS
Solver --> SQL : SQL / TCP, TLS
Export --> Ext : HTTPS / REST

note bottom of App
  АК-01: страница расписания ≤ 2 с для 95% запросов
  АК-03: 200 пользователей, ответов 5xx ≤ 1%
end note
@enduml
"))
