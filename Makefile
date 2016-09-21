.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

FIG_SIZE := 0.29

PROCESSED=data/processed
SENSORS=src/sensors/sensors.yaml
PROCESSED_CALI = $(PROCESSED)/$(CALI_SETTINGS)
CALI_SETTINGS=calibration
CALI_YAML=$(shell find $(CALI_SETTINGS)/ -name '*.yaml')
CALI_TEX=$(patsubst %.yaml,%.tex,$(addprefix $(PROCESSED)/,$(CALI_YAML)))
CALI_REPORT = $(patsubst %.tex,%.pdf,$(CALI_TEX))
CALI_TEMPLATE=$(CALI_SETTINGS)/cali.tpl
PROCESSED_CALI_EXP=$(patsubst %.yaml,%.json,$(addprefix $(PROCESSED)/,$(CALI_YAML)))
CALIBRATION_SCRIPT := -m src.calibration

DYLOS_SETTINGS=dylos
DYLOS_YAML=$(shell find $(DYLOS_SETTINGS)/ -name '*.yaml')
DYLOS_TEX=$(patsubst %.yaml,%.tex,$(addprefix $(PROCESSED)/,$(DYLOS_YAML)))
DYLOS_REPORT = $(patsubst %.tex,%.pdf,$(DYLOS_TEX))
DYLOS_TEMPLATE=$(DYLOS_SETTINGS)/dylos.tpl
PROCESSED_DYLOS=$(patsubst %.yaml,%.json,$(addprefix $(PROCESSED)/,$(DYLOS_YAML)))
DYLOS_SCRIPT := -m src.sensors.dylos-plots

DATA := $(shell find data/raw/ -name '*.log')

GEN_SCRIPT := -m src.docs.gen

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

docs: requirements

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
$(PROCESSED)/$(CALI_SETTINGS)/%.json: $(CALI_SETTINGS)/%.yaml $(SENSORS) $(DATA)
	python $(CALIBRATION_SCRIPT) $< $(SENSORS) -o $@ -f $(FIG_SIZE)

$(PROCESSED)/$(CALI_SETTINGS)/%.tex: $(PROCESSED)/$(CALI_SETTINGS)/%.json $(CALI_TEMPLATE)
	python $(GEN_SCRIPT) $(CALI_TEMPLATE) $< $@ 

# Dylos report
$(PROCESSED)/$(DYLOS_SETTINGS)/%.json: $(DYLOS_SETTINGS)/%.yaml $(DATA)
	python $(DYLOS_SCRIPT) $< -o $@ -f $(FIG_SIZE)

$(PROCESSED)/$(DYLOS_SETTINGS)/%.tex: $(PROCESSED)/$(DYLOS_SETTINGS)/%.json $(DYLOS_TEMPLATE)
	python $(GEN_SCRIPT) $(DYLOS_TEMPLATE) $< $@ 

# generate PDF
%.pdf: %.tex
	FILE=$(notdir $*)
	cd $(dir $*); \
	latexmk -pdf -pv -pdflatex="pdflatex --shell-escape -halt-on-error %O %S" $(notdir $*); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	@echo $*

