# ГОСТ Typst

Набор для отчётов по ГОСТ 7.32 в Typst. Оформление страницы — пакет [`modern-g7-32`](https://typst.app/universe/package/modern-g7-32). Сюда входит раскладка файлов, хелперы и скрипты.

`Пример работы с Typst.typ` — синтаксис элементов ГОСТ в одном файле. Корень отчёта только собирает, текст — в каталоге этого отчёта.

## Установка в проект

Архив `gost-typst-Report-vX.Y.Z.zip` с тега `v*` распаковывается в `Report/` рядом с исходниками.

```bash
mkdir -p Report && unzip -o gost-typst-Report-v1.0.0.zip -d Report
```

`Пример работы с Typst.typ` — справочник синтаксиса ГОСТ (`figure` + `table`); таблицы в `includes/common.typ` устроены так же. `extras/` — преамбула практики и обёртка короткого PDF.

В архиве нет `.git`, `.gitea`, `dist/`, `*.pdf`, `__pycache__` и `listings/generated/`.

```
Report/
  includes/                  ← один раз на проект
    common.typ               ← таблицы, рисунки, заголовки
    title-page-mop-evm.typ   ← бланк кафедры МОП ЭВМ (ЮФУ+ИКТИБ+МОП ЭВМ)
    title-page-prikladnaya-informatika.typ ← бланк ПИ (ЮФУ+ИКТИБ)
    title-page-common.typ    ← общие куски бланков (подписи, оценка, шапка)
    title-page.typ           ← реэкспорт МОП ЭВМ
    pz-pagination.typ
    pz-page-offset.typ       ← счётчик страниц при склейке PDF-титула
    listings-appendix.typ
  reports/
    primer/                  ← один отчёт; следующий — соседний каталог
      report.typ             ← корень: gost, include, bibliography
      meta.typ               ← тема, УДК, студент, кафедра
      intro.typ, ch01.typ, … ← разделы: один файл — один заголовок уровня 1
      references.bib
      appendices/
  extras/                    ← практика и короткий PDF
  Пример работы с Typst.typ  ← синтаксис элементов ГОСТ
  listings/listings.config.yaml
  images/                    ← файлы для pz-fig
  images/logos/              ← sfedu, iktib, mop-evm (SOURCES.md)
  puml/fig_*.puml
  scripts/
```

Хелперы и бланки общие. Новый отчёт — каталог `reports/<имя>/` со своим `report.typ` и `meta.typ`. Главы `primer/` — текст примера.

## Правила

1. В `reports/<имя>/report.typ` нет абзацев глав — только `#show: gost.with`, `#include`, `#outline()`, `#bibliography`, приложения.
2. Глава начинается с `= …`. Введение и заключение: `#heading(numbering: none, outlined: true)[Введение]`.
3. Аннотация и «Обозначения» — `pz-front-heading`, не `= …` (иначе `gost` вставит разрыв страницы).
4. Рисунки: `#pz-fig("fig_01.png", [Подпись], "fig-01")` → `images/fig_01.png`. Диаграммы сначала в `puml/`, затем `render_puml.sh`.
5. Таблицы: `pz-table` / `pz-test-table`. В тексте среднее тире «–», не «—» (`scripts/check_gost_dashes.py` проверяет все `*.typ`, кроме `listings/`, `extras/`, `puml/`, `scripts/` и файла-примера).
6. Большую главу дробите include **из файла главы**, не из корня.
7. Листинги не писать вручную — `listings.config.yaml` + `gen_listings.py`.

Корень отчёта — `reports/<имя>/report.typ`. Образец `reports/primer` на бланке ПИ: `hide-title: true` и `#pz-title-page(meta)`. Бланк МОП ЭВМ — другой `#import` и поле `department` в `meta.typ`. Другая кафедра — скопировать `title-page-mop-evm.typ` → `title-page-<кафедра>.typ`, сменить ряд логотипов и `#import` в корне отчёта. Типовой ГОСТ-титул пакета: `hide-title: false` без вызова бланка. Готовый PDF-титул кафедры: `hide-title: true`, `#include` page-offset, `FRONT_PDF=… ./scripts/build.sh`.

В `common.typ` есть `pz-biblio-strip-en` (английская библиографическая полоска). Образца `abstract-en.typ` в наборе нет — при необходимости добавьте сами по образцу `abstract-ru.typ`.

## Сборка

```bash
cd Report
./scripts/build.sh
python3 scripts/gen_listings.py              # если есть приложение с кодом
./scripts/render_puml.sh                     # если есть puml/fig_*.puml
python3 scripts/compress_screenshots.py      # опционально: сжать скриншоты
```

`build.sh` сначала вызывает `check_gost_dashes.py`, затем `typst compile`. Переменные окружения:

| Переменная | По умолчанию | Назначение |
|------------|--------------|------------|
| `REPORT_TYP` | `reports/primer/report.typ` | Корневой `.typ` |
| `OUT_PDF` | PDF рядом с этим `.typ` | Итоговый PDF |
| `FRONT_PDF` | (пусто) | PDF титула для склейки через `qpdf`; без неё — обычная компиляция |
| `FRONT_PAGES` | `3` | Сколько страниц взять из `FRONT_PDF` (совпадает с `pz-page-offset.typ`) |

`compress_screenshots.py` жмёт все JPEG/PNG в `images/`, кроме файлов, чьи стемы совпадают с `puml/*.puml` (диаграммы не трогает). Пустой набор — не ошибка.

### Зависимости

- Typst, Times New Roman
- диаграммы: Java, PlantUML
- склейка титула: `qpdf`
- листинги: PyYAML (`pip install pyyaml`)
- сжатие скриншотов: ImageMagick (`magick` или `convert`), `pngquant`

### `listings.config.yaml`

Образец короче полного набора ключей. Скрипт понимает в том числе:

- `scan_root` — корень обхода исходников (относительно `Report/`)
- `include_extensions` — суффикс → язык `raw`
- `include_filenames` — имя файла → язык (без расширения в ключе не требуется)
- `root_build_files` — файлы корня репозитория в группу `root`
- `exclude_dirs`, `exclude_globs`
- `modules_order`, `module_titles`
- `pagebreak_per_module`, `pagebreak_per_file`, `pagebreak_after_listing`
- `only_path_substrings`, `only_test_filenames`
- `generated_subdir`, `appendix_filename`, `caption_prefix`

## Релиз

Тег `v*` запускает `.gitea/workflows/release.yml`: скрипт `scripts/pack-report-release.sh` собирает zip и workflow публикует его в Releases.

```bash
git tag v1.0.0
git push origin v1.0.0
```

Локально, без публикации: `./scripts/pack-report-release.sh 1.0.0` → `dist/gost-typst-Report-v1.0.0.zip`.

Публикация идёт секретом `ACCOUNT_TOKEN`: личный токен доступа (Настройки → Приложения). Ему нужно одно разрешение: **repository — Read and Write** (`write:repository`). Им создаётся релиз и загружается zip. Разрешения `package`, `admin` и `all` не нужны. Если репозиторий закрытый, у токена снимают «Public only». Учётная запись токена должна иметь право записи в репозиторий.

## extras/

Короткие PDF отдельно от пояснительной записки:

- `practice-preamble.typ` — преамбула отчёта по практике: поля `practice_meta` (вид, сроки, организация, студент, группа, направление, проект) и заголовок `practice_title`
- `fragment-doc.typ` — обёртка фрагмента/методички без ГОСТ-титула: параметры `title`, `criterion`, `work-title`; шрифт 14 pt, отступ 1,25 см, заголовки уровней 1–2

## Новый отчёт

1. Скопировать `reports/primer/` в `reports/<имя>/`.
2. Заполнить `meta.typ` и `gost.with` в `report.typ` этого каталога.
3. Заменить главы и строку `#include`. Текст разделов остаётся рядом с `report.typ`.
4. Собрать: `REPORT_TYP=reports/<имя>/report.typ ./scripts/build.sh`.
5. Синтаксис таблицы и рисунка — в `Пример работы с Typst.typ`.

Общими остаются `includes/`, `scripts/` и `images/logos/`.
