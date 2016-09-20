.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

RAW := data/raw
PROCESSED := data/processed
INTERIM := data/interim
SENSORS := src/sensors/sensors.yaml
SETTINGS := settings

DATA := $(shell find $(RAW)/ -name '*.log')
YAML := $(shell find $(SETTINGS)/ -name '*.yaml')
INTERIM_DATA := $(addprefix $(INTERIM)/,$(notdir $(patsubst %.yaml,%.json,$(YAML))))

PROCESS_SCRIPT := src/data/process.py

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

docs: requirements

data: $(INTERIM_DATA)

cleandata:
	rm -rf $(INTERIM)/*

clean: cleandata
	find . -name "*.pyc" -exec rm {} \;

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

$(INTERIM_DATA): $(PROCESS_SCRIPT) $(YAML) $(SENSORS) $(DATA)
	python $(PROCESS_SCRIPT) $(YAML) $(SENSORS) $(RAW) -o $@

# generate PDF
%.pdf: %.tex
	FILE=$(notdir $*)
	cd $(dir $*); \
	latexmk -pdf -pv -pdflatex="pdflatex --shell-escape -halt-on-error %O %S" $(notdir $*); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	@echo $*

