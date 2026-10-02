PYTHON ?= python
QGIS_PREFIX ?= /usr

DATA := CR_Bikeways.json
ROUTES := site_routes.txt
SCRIPT := export_bikeway_maps.py

REVIEW_DIR := review
SITE_BUILD_DIR := .site-build
SITE_MAP_DIR := ../../docs/maps/bikeways
NOTES_DIR := ../../notes

.PHONY: help review site list clean

help:
	@echo "make review  - export all routes to review/ with numbered filenames + index.html"
	@echo "make site    - export only site_routes.txt to docs/maps/bikeways/ and rebuild gettingaround.html"
	@echo "make list    - show the route grouping without rendering PNGs"
	@echo "make clean   - remove local review/build output (published maps are left alone)"

review:
	$(PYTHON) $(SCRIPT) \
		--input $(DATA) \
		--output $(REVIEW_DIR) \
		--merge-file $(ROUTES) \
		--prefix-path $(QGIS_PREFIX)
	@echo
	@echo "Open $(REVIEW_DIR)/index.html in a browser."

site:
	mkdir -p $(SITE_MAP_DIR)
	rm -f $(SITE_MAP_DIR)/*.png $(SITE_MAP_DIR)/manifest.csv
	$(PYTHON) $(SCRIPT) \
		--input $(DATA) \
		--output $(SITE_BUILD_DIR) \
		--site-output $(SITE_MAP_DIR) \
		--merge-file $(ROUTES) \
		--merge-file-only \
		--prefix-path $(QGIS_PREFIX)
	$(MAKE) -C $(NOTES_DIR) gettingaround
	@echo
	@echo "Published bikeway assets are in $(SITE_MAP_DIR)."
	@echo "gettingaround.html has been rebuilt. Inspect git diff before committing."

list:
	$(PYTHON) $(SCRIPT) \
		--input $(DATA) \
		--output $(REVIEW_DIR) \
		--merge-file $(ROUTES) \
		--prefix-path $(QGIS_PREFIX) \
		--list-only

clean:
	rm -rf $(REVIEW_DIR) $(SITE_BUILD_DIR) __pycache__
