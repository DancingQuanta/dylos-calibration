.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROCESSED=data/processed
SENSORS=src/sensors/sensors.yaml
CALI_SETTINGS=calibration
CALI_YAML=$(shell find $(CALI_SETTINGS)/ -name '*.yaml')
CALI_TEX=$(patsubst %.yaml,%.tex,$(addprefix $(PROCESSED)/,$(CALI_YAML)))
CALI_REPORT = $(patsubst %.tex,%.pdf,$(CALI_TEX))
CALI_TEMPLATE=calibration/cali.tpl
PROCESSED_CALI_EXP=$(patsubst %.yaml,%.json,$(addprefix $(PROCESSED)/,$(CALI_YAML)))

DYLOS_SETTINGS=dylos
DYLOS_YAML=$(shell find $(DYLOS_SETTINGS)/ -name '*.yaml')
DYLOS_TEX=$(patsubst %.yaml,%.tex,$(addprefix $(PROCESSED)/,$(DYLOS_YAML)))
DYLOS_REPORT = $(patsubst %.tex,%.pdf,$(DYLOS_TEX))
DYLOS_TEMPLATE=$(DYLOS_SETTINGS)/dylos.tpl
PROCESSED_DYLOS=$(patsubst %.yaml,%.json,$(addprefix $(PROCESSED)/,$(DYLOS_YAML)))

DATA := $(shell find data/raw/ -name '*.log')

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

docs: requirements
	@mkdocs serve & echo "$$!" > "mkdocs-pid"

data: 
	python -m src.data.inspect_data

dylos: $(PROCESSED_DYLOS) $(DYLOS_REPORT)

devcali: $(PROCESSED_CALI_EXP)

cali: $(CALI_REPORT) $(PROCESSED_CALI_EXP)

clean: cleancali
	find . -name "*.pyc" -exec rm {} \;

cleancali: 
	-rm -rf $(PROCESSED_CALI_EXP) $(CALI_TEX) $(CALI_REPORT)

recali: cleancali cali

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

# Generate a report for calibration
$(PROCESSED_CALI_EXP): $(CALI_YAML) $(SENSORS) $(DATA)
	python -m src.calibration $< $(SENSORS) -o $@

$(CALI_TEX): $(PROCESSED_CALI_EXP) $(CALI_TEMPLATE)
	python -m src.docs.gen $(CALI_TEMPLATE) $< $@ 

# Dylos report
$(PROCESSED_DYLOS): $(DYLOS_YAML) $(DATA)
	python -m src.dylos $< -o $@

$(DYLOS_TEX): $(PROCESSED_DYLOS) $(DYLOS_TEMPLATE)
	python -m src.docs.gen $(DYLOS_TEMPLATE) $< $@ 

# generate PDF
%.pdf: %.tex
	FILE=$(notdir $*)
	cd $(dir $*); \
	latexmk -pdf -pv -pdflatex="pdflatex --shell-escape -halt-on-error %O %S" $(notdir $*); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	@echo $*

