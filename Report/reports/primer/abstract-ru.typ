#import "meta.typ": meta
#import "../../includes/common.typ": pz-biblio-strip-ru, pz-front-heading

#pz-biblio-strip-ru(
  udk: meta.udk,
  author: meta.author,
  title: meta.topic,
  year: int(meta.year),
)

#pz-front-heading(page-break: false)[Аннотация]

#{
  set par(first-line-indent: 1.25cm, justify: true)

  [Отчёт описывает учебный каркас набора Typst для оформления пояснительных записок по ГОСТ 7.32. Показаны раскладка файлов, роль корневого `report.typ`, текст отчёта рядом с ним, общие хелперы с префиксом `pz-` в `includes/` и сборка PDF скриптом `scripts/build.sh`.]

  parbreak()

  [Пакет `@preview/modern-g7-32` не вендорится: Typst подключает его через `#import`. Аннотация и обозначения оформляются через `pz-front-heading`, чтобы шаблон `gost` не добавлял лишний разрыв страницы. В приложениях приведён краткий перечень каталогов набора.]
}
