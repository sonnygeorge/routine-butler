# Makefile

# Create virtual environment
venv:
	python3 -m venv venv

# Activate virtual environment
activate:
	source venv/bin/activate

# Install requirements
install:
	pip install -r requirements.txt

# Run app
run:
	python3 run.py

# Clean up repo junk files
cleanse:
	@echo "Cleaning up junk files..."
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.DS_Store' -delete
	find . -name '.pytest_cache' -exec rm -rf {} +
	@echo "Cleanup complete."
