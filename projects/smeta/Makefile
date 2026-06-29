install:
	pip install -r requirements.txt

eval:
	python3 src/eval_smeta.py --smeta $(SMETA) --vor $(VOR) --region "$(REGION)" --quarter "$(QUARTER)"

template:
	python3 src/create_bim_template.py --output $(OUTPUT) --region $(REGION) --year $(YEAR) --quarter $(Q)

check-updates:
	bash scripts/check_updates.sh

status:
	@echo "=== Smeta Project Status ==="
	@echo "Version: $(shell cat manifest.json | grep -o '"version": "[^"]*"' | cut -d'"' -f4)"
	@echo "Last updated: $(shell cat config/indexes.json | grep last_updated | cut -d'"' -f4)"
	@echo "Next check: $(shell cat config/indexes.json | grep next_check | cut -d'"' -f4)"
	@echo "Objects: $(shell ls data/ | wc -l)"
	@echo "=========================="

.PHONY: install eval template check-updates status
