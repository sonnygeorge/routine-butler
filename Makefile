# Makefile

# Create virtual environment
venv:
	python3 -m venv venv

# Activate virtual environment
activate:
	source venv/bin/activate

# Clean up repo junk files
cleanse:
	@echo "Cleaning up junk files..."
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.DS_Store' -delete
	find . -name '.pytest_cache' -exec rm -rf {} +
	@echo "Cleanup complete."

# Show status of systemd routine_butler.service
status:
	sudo systemctl status routine_butler.service

# Show journal of systemd routine_butler.service
journal:
	sudo journalctl --pager-end -u routine_butler.service
