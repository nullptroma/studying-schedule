.PHONY: отчёт-01 отчёт-02 отчёт-03 диаграммы

отчёт-01:
	python3 скрипты/собрать-отчёт-01.py
	cd Report && REPORT_TYP=reports/01-верификация/report.typ ./scripts/build.sh

отчёт-02:
	python3 скрипты/собрать-отчёт-02.py
	cd Report && PUML_PNG_QUALITY=70-90 ./scripts/render_puml.sh
	cd Report && PUML_PNG_QUALITY=70-90 ./scripts/fix_dfd_arrowheads.sh
	cd Report && REPORT_TYP=reports/02-моделирование/report.typ ./scripts/build.sh

отчёт-03:
	python3 скрипты/собрать-отчёт-03.py
	cd Report && REPORT_TYP=reports/03-case/report.typ ./scripts/build.sh

диаграммы:
	cd Report && ./scripts/render_puml.sh
