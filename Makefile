.PHONY: отчёт-01 диаграммы

отчёт-01:
	python3 скрипты/собрать-отчёт-01.py
	cd Report && REPORT_TYP=reports/01-верификация/report.typ ./scripts/build.sh

диаграммы:
	cd Report && ./scripts/render_puml.sh
