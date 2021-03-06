.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

FIG_SIZE := 0.29

RAW := data/raw
PROCESSED := data/processed
INTERIM := data/interim
IMGS := imgs/plots
SENSORS := conditions/sensors.yaml
PARTICLES := conditions/particles.yaml
SETTINGS := settings

DATA := $(shell find $(RAW)/ -name '*.log')
YAML := $(shell find $(SETTINGS)/ -name '*.yaml')
INTERIM_SETTINGS := $(patsubst $(SETTINGS)/%.yaml,$(INTERIM)/%.json,$(YAML))
INTERIM_DATA := $(shell find $(INTERIM)/ -name '*.csv')
REBINNED_FLAGS := $(patsubst $(INTERIM)/%.json,.rebinned-%,$(INTERIM_SETTINGS))

PLOT_DATA := $(patsubst $(INTERIM)/%.csv,$(IMGS)/%-plot.png,$(INTERIM_DATA))
PLOT_MAT := $(patsubst $(INTERIM)/%.json,$(IMGS)/%-plot-mat.png,$(INTERIM_SETTINGS))
PLOT_MAT_PDF := $(patsubst $(INTERIM)/%.json,$(PROCESSED)/%-plot-mat.pdf,$(INTERIM_SETTINGS))
PLOT_MAT_TEMPLATE := templates/plot_mat.tpl

HIST_PLOT := $(patsubst $(INTERIM)/%.csv,$(IMGS)/%-hist.png,$(INTERIM_DATA))
HIST_STATS := $(patsubst $(INTERIM)/%.csv,$(PROCESSED)/%-stats.tex,$(INTERIM_DATA))
HIST_MAT := $(patsubst $(INTERIM)/%.json,$(IMGS)/%-hist-mat.png,$(INTERIM_SETTINGS))
HIST_MAT_PDF := $(patsubst $(INTERIM)/%.json,$(PROCESSED)/%-hist-mat.pdf,$(INTERIM_SETTINGS))
HIST_MAT_TEMPLATE := templates/hist_mat.tpl

CALI_MAT := $(patsubst $(INTERIM)/%.json,$(IMGS)/%-cali-mat.png,$(INTERIM_SETTINGS))
CALI_MAT_PDF := $(patsubst $(INTERIM)/%.json,$(PROCESSED)/%-cali-mat.pdf,$(INTERIM_SETTINGS))
CALI_MAT_TEMPLATE := templates/cali_mat.tpl

FULL_REPORT := $(patsubst $(INTERIM)/%.json,$(PROCESSED)/%.pdf,$(INTERIM_SETTINGS))
FULL_TEMPLATE := templates/calibration.tpl

PROCESS_SCRIPT := src/data/process.py
REBIN_SCRIPT := src/data/rebin_data.py
PLOT_SCRIPT := src/visualisation/plot.py
PLOT_MAT_SCRIPT := src/visualisation/plot_matrix.py
HIST_SCRIPT := src/visualisation/hist.py
HIST_MAT_SCRIPT := src/visualisation/hist_matrix.py
CALI_MAT_SCRIPT := src/visualisation/calibration.py
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

analyse: $(FULL_REPORT)

rebin: $(REBINNED_FLAGS)

plot: $(PLOT_DATA)

plotmat: $(PLOT_MAT_PDF)

hist: $(HIST_PLOT)

histmat: $(HIST_MAT_PDF)

calibrate: $(CALI_MAT_PDF)

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

$(INTERIM)/%.json: $(SETTINGS)/%.yaml $(SENSORS) $(PARTICLES) $(DATA) $(PROCESS_SCRIPT)
	python $(PROCESS_SCRIPT) $< $(SENSORS) $(PARTICLES) $(RAW) -o $@

.rebinned-%: $(INTERIM)/%.json $(REBIN_SCRIPT)
	python $(REBIN_SCRIPT) $<
	touch .rebinned-$*

# Time series plots
$(IMGS)/%-plot.png: $(INTERIM)/%.csv $(PLOT_SCRIPT)
	python $(PLOT_SCRIPT) $< -o $@ -f $(FIG_SIZE)

$(IMGS)/%-plot-mat.png: $(INTERIM)/%.json $(REBINNED_FLAGS) $(PLOT_MAT_SCRIPT)
	python $(PLOT_MAT_SCRIPT) $< -o $@

$(PROCESSED)/%-plot-mat.tex: $(INTERIM)/%.json $(PLOT_MAT_TEMPLATE) $(PLOT_MAT)
	python $(GEN_SCRIPT) $(PLOT_MAT_TEMPLATE) $< $@ 

# Histogram plots
$(IMGS)/%-hist.png $(PROCESSED)/%-hist.csv: $(INTERIM)/%.csv $(HIST_SCRIPT)
	python $(HIST_SCRIPT) $< -p $(IMGS)/$*-hist.png -s $(PROCESSED)/$*-hist.csv -f $(FIG_SIZE)

$(IMGS)/%-hist-mat.png: $(INTERIM)/%.json $(REBINNED_FLAGS) $(HIST_MAT_SCRIPT)
	python $(HIST_MAT_SCRIPT) $< -o $@

$(PROCESSED)/%-hist-mat.tex: $(INTERIM)/%.json $(HIST_MAT_TEMPLATE) $(HIST_MAT)
	python $(GEN_SCRIPT) $(HIST_MAT_TEMPLATE) $< $@ 

# Calibration
$(IMGS)/%-cali-mat.png $(PROCESSED)/%-cali.tex: $(INTERIM)/%.json $(REBINNED_FLAGS) $(CALI_MAT_SCRIPT)
	python $(CALI_MAT_SCRIPT) $< -p $(IMGS)/$*-cali-mat.png -s $(PROCESSED)/$*-cali.tex

$(PROCESSED)/%-cali-mat.tex: $(INTERIM)/%.json $(CALI_MAT_TEMPLATE) $(CALI_MAT)
	python $(GEN_SCRIPT) $(CALI_MAT_TEMPLATE) $< $@ 

# Overall
$(PROCESSED)/%.tex: $(INTERIM)/%.json $(FULL_TEMPLATE) $(PLOT_MAT) $(HIST_MAT) $(CALI_MAT)
	python $(GEN_SCRIPT) $(FULL_TEMPLATE) $< $@ 

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
