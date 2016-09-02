.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROCESSED=data/processed/
SENSORS=src/sensors/sensors.yaml
CALI_SETTINGS=$(shell find calibration/ -name '*.yaml')
CALI_REPORT = $(patsubst %.tex,%.pdf,$(CALI_TEX))
CALI_TEX=$(patsubst %.yaml,%.tex,$(addprefix $(PROCESSED),$(CALI_SETTINGS)))
CALI_TEMPLATE=calibration/cali.tpl
PROCESSED_CALI_EXP=$(patsubst %.yaml,%.json,$(addprefix $(PROCESSED),$(CALI_SETTINGS)))
CALI_DATA := $(shell find data/raw/ -name '*.log')

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

docs: requirements
	@mkdocs serve & echo "$$!" > "mkdocs-pid"

data: 
	python -m src.data.inspect_data

dylos: 
	python -m src.visualization.dylos

devcali: $(PROCESSED_CALI_EXP)

cali: $(CALI_REPORT) $(PROCESSED_CALI_EXP)

clean: cleancali
	find . -name "*.pyc" -exec rm {} \;

cleancali: 
	-rm $(PROCESSED_CALI_EXP) $(CALI_REPORT) $(CALI_TEX)

recali: cleancali cali

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

# Generate a report for calibration
$(PROCESSED_CALI_EXP): $(CALI_SETTINGS) $(SENSORS) $(CALI_DATA)
	python -m src.calibration $(CALI_SETTINGS) $(SENSORS) -o $(PROCESSED_CALI_EXP)

$(CALI_TEX): $(CALI_TEMPLATE) $(PROCESSED_CALI_EXP)
	python -m src.docs.gen $^ $@ 

# generate PDF
%.pdf: %.tex
	FILE=$(notdir $*)
	cd $(dir $*); \
	latexmk -pdf -pv -pdflatex="pdflatex --shell-escape -halt-on-error %O %S" $(notdir $*); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	@echo $*

