.PHONY: help m1-up m1-down m1-ingest m2-up m2-down m3-up m3-upload tree

help:
	@echo "Targets:"
	@echo "  m1-up       Start Module 01 services (db + pgadmin)"
	@echo "  m1-down     Stop Module 01 services"
	@echo "  m1-ingest   Run Module 01 ingestion containers"
	@echo "  m2-up       Start Airflow stack (Module 02)"
	@echo "  m2-down     Stop Airflow stack (Module 02)"
	@echo "  m3-upload   Upload Module 03 parquet files to GCS via Docker uploader"
	@echo "  tree        Show repo tree (depth 3)"

# ---- Module 01 ----
m1-up:
	cd module_01_docker_terraform && docker compose up -d db pgadmin

m1-down:
	cd module_01_docker_terraform && docker compose down

m1-ingest:
	cd module_01_docker_terraform && docker compose run --rm ingest_zones
	cd module_01_docker_terraform && docker compose run --rm ingest_green

# ---- Module 02 ----
m2-up:
	cd module_02_workflow_orchestration/airflow && docker compose up -d

m2-down:
	cd module_02_workflow_orchestration/airflow && docker compose down

# ---- Module 03 ----
m3-upload:
	cd module_03_data_warehouse && docker compose build
	cd module_03_data_warehouse && docker compose run --rm uploader

tree:
	tree -L 3