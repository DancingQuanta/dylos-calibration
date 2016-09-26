.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

FIG_SIZE := 0.29

RAW := data/raw
PROCESSED := data/processed
INTERIM := data/interim
IMGS := imgs/plots
SENSORS := src/sensors/sensors.yaml
SETTINGS := settings

DATA := $(shell find $(RAW)/ -name '*.log')
YAML := $(shell find $(SETTINGS)/ -name '*.yaml')
INTERIM_SETTINGS := $(patsubst $(SETTINGS)/%.yaml,$(INTERIM)/%.json,$(YAML))
INTERIM_DATA := $(shell find $(INTERIM)/ -name '*.csv')
CALIBRATE_FLAGS := $(patsubst $(INTERIM)/%.json,.calibrated-%,$(INTERIM_SETTINGS))

PLOT_DATA := $(patsubst $(INTERIM)/%.csv,$(IMGS)/%-plot.png,$(INTERIM_DATA))
PLOT_MAT := $(patsubst $(INTERIM)/%.json,$(IMGS)/%-plot-mat.png,$(INTERIM_SETTINGS))
PLOT_MAT_PDF := $(patsubst $(INTERIM)/%.json,$(PROCESSED)/%-plot-mat.pdf,$(INTERIM_SETTINGS))
PLOT_MAT_TEMPLATE := templates/plot_mat.tpl

HIST_PLOT := $(patsubst $(INTERIM)/%.csv,$(IMGS)/%-hist.png,$(INTERIM_DATA))
HIST_STATS := $(patsubst $(INTERIM)/%.csv,$(PROCESSED)/%-stats.tex,$(INTERIM_DATA))
HIST_MAT := $(patsubst $(INTERIM)/%.json,$(IMGS)/%-hist-mat.png,$(INTERIM_SETTINGS))
HIST_MAT_PDF := $(patsubst $(INTERIM)/%.json,$(PROCESSED)/%-hist-mat.pdf,$(INTERIM_SETTINGS))
HIST_MAT_TEMPLATE := templates/hist_mat.tpl

PROCESS_SCRIPT := src/data/process.py
CALIBRATION_SCRIPT := src/data/calibration.py
PLOT_SCRIPT := src/visualisation/plot.py
PLOT_MAT_SCRIPT := src/visualisation/plot_matrix.py
HIST_SCRIPT := src/visualisation/hist.py
HIST_MAT_SCRIPT := src/visualisation/hist_matrix.py
GEN_SCRIPT := src/docs/gen.py

FIGURES := $(shell find $(IMGS)/ -name '*.pgf')

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

calibrate: $(CALIBRATE_FLAGS)

plot: $(PLOT_DATA)

plotmat: $(PLOT_MAT_PDF)

hist: $(HIST_PLOT)

histmat: $(HIST_MAT_PDF)

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

.calibrated-%: $(INTERIM)/%.json $(CALIBRATION_SCRIPT)
	python $(CALIBRATION_SCRIPT) $<
	touch .calibrated-$*

# Time series plots
$(IMGS)/%-plot.png: $(INTERIM)/%.csv $(PLOT_SCRIPT)
	python $(PLOT_SCRIPT) $< -o $@ -f $(FIG_SIZE)

$(IMGS)/%-plot-mat.png: $(INTERIM)/%.json $(DATA) $(PLOT_MAT_SCRIPT)
	python $(PLOT_MAT_SCRIPT) $< -o $@

$(PROCESSED)/%-plot-mat.tex: $(INTERIM)/%.json $(PLOT_MAT_TEMPLATE) $(PLOT_MAT)
	python $(GEN_SCRIPT) $(PLOT_MAT_TEMPLATE) $< $@ 

# Histogram plots
$(IMGS)/%-hist.png $(PROCESSED)/%-hist.csv: $(INTERIM)/%.csv $(HIST_SCRIPT)
	python $(HIST_SCRIPT) $< -p $(IMGS)/$*-hist.png -s $(PROCESSED)/$*-hist.csv -f $(FIG_SIZE)

$(IMGS)/%-hist-mat.png: $(INTERIM)/%.json $(DATA) $(HIST_MAT_SCRIPT)
	python $(HIST_MAT_SCRIPT) $< -o $@

$(PROCESSED)/%-hist-mat.tex: $(INTERIM)/%.json $(HIST_MAT_TEMPLATE) $(HIST_MAT)
	python $(GEN_SCRIPT) $(HIST_MAT_TEMPLATE) $< $@ 

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
