.PHONY: setup run clean docker-build

setup:
	pip install -r requirements.txt
	pip install -e .

run:
	python -m src.healing_pipeline.cli

clean:
	rm -rf __pycache__ .pytest_cache
	rm -f recovery.log
	find . -type d -name "__pycache__" -exec rm -rf {} +

docker-build:
	docker build -t healing-pipeline .
