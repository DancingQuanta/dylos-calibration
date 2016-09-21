.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

RAW := data/raw
PROCESSED := data/processed
INTERIM := data/interim
IMGS := imgs
SENSORS := src/sensors/sensors.yaml
SETTINGS := settings

DATA := $(shell find $(RAW)/ -name '*.log')
YAML := $(shell find $(SETTINGS)/ -name '*.yaml')
INTERIM_SETTINGS := $(addprefix $(INTERIM)/,$(notdir $(patsubst %.yaml,%.json,$(YAML))))
INTERIM_DATA := $(shell find $(INTERIM)/ -name '*.csv')
PLOT_DATA := $(patsubst $(INTERIM)/%-plot.csv,$(IMGS)/%.png,$(INTERIM_DATA))
HIST_DATA := $(patsubst $(INTERIM)/%-hist.csv,$(IMGS)/%.png,$(INTERIM_DATA))

PROCESS_SCRIPT := src/data/process.py
CALIBRATION_SCRIPT := src/data/calibration.py
PLOT_SCRIPT := src/visualisation/plot.py

# Tikz
TIKZ := $(shell find $(IMGS)/ -name '*.tikz')
TIKZPDF = $(patsubst %.tikz,%.pdf,$(TIKZ))

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

docs: requirements

data: $(INTERIM_SETTINGS)

calibrate: $(INTERIM_SETTINGS)

plot: $(PLOT_DATA)

figures: $(TIKZPDF)

cleandata:
	rm -rf $(INTERIM)/*

clean: cleandata
	find . -name "*.pyc" -exec rm {} \;

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

$(INTERIM)/%.json: $(SETTINGS)/%.yaml $(SENSORS) $(DATA) $(PROCESS_SCRIPT)
	python $(PROCESS_SCRIPT) $< $(SENSORS) $(RAW) -o $@

$(INTERIM)/%.json: $(INTERIM)/%.json $(DATA) $(CALIBRATION_SCRIPT)
	python $(CALIBRATION_SCRIPT) $< -o $@

$(IMGS)/%.png: $(INTERIM)/%.csv $(PLOT_SCRIPT)
	python $(PLOT_SCRIPT) $< -o $@

# Generate PDF from TIKZ
%.pdf: %.tikz $(FIGURES)
	FILE=$(notdir $<)
	cd $(dir $<); \
	pdflatex $(notdir $<); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk
	@echo $<

# generate PDF
%.pdf: %.tex
	FILE=$(notdir $*)
	cd $(dir $*); \
	latexmk -pdf -pv -pdflatex="pdflatex --shell-escape -halt-on-error %O %S" $(notdir $*); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	@echo $*
