##############################################################################
#	
#	author: Andrew Tolmie
#
#	date: 06/07/15
#
#	description: Makefile to turn a collection of markdown files into one pdf
#	The pdf generation is done with latexmk
#	The markdown files are stored in /md/ folder
#	The bib references are stored in /references/ folder
#	The figures are stored in /figures/
#
##############################################################################

SOURCE = md
MD = $(wildcard $(SOURCE)/*.md)
NAME = $(notdir $(MD))
TEX = $(patsubst %.md,%.tex,$(NAME))
PDF = $(patsubst %.md,%.pdf,$(NAME))
YAML = report.yaml
FIGURES = figures

## Figures

# SVG to PDF with TEX
SVG := $(shell find $(FIGURES) -name '*.svg')
PDF_SVG = $(patsubst %.svg,%.pdf,$(SVG))
PDF_TEX = $(patsubst %.svg,%.pdf_tex,$(SVG))
PNG_SVG = $(patsubst %.svg,%.png,$(SVG))

# Tikz
TIKZ := $(shell find $(FIGURES) -name '*.tikz')
TIKZPDF = $(patsubst %.tikz,%.pdf,$(TIKZ))

FIGURES := $(shell find figures/* -type f)

# Pandoc
TEMPLATE = $(shell cygpath -w -a $(HOME)/.pandoc/tex/report.tex)
PANDOC_OPTS = -s --listings --filter pandoc-eqnos --filter pandoc-fignos --filter pandoc-tablenos --template=$(TEMPLATE)
#--filter pandoc-citeproc

# Latexmk
LATEX=pdflatex
LATEXOPT=--shell-escape
NONSTOP=-halt-on-error
#NONSTOP=--interaction=errorstopmode

.PHONY: all clean figures tex pdf report bib

all: figures tex pdf

figures: $(PNG_SVG) $(PDF_SVG) $(TIKZPDF)

tex: $(TEX)

pdf: $(PDF)

bib: report.bib

report: report.pdf

# Cat bib files into one
# bibtex
# Use backstash \ for every line
BIBDIR=references
BIBFILE=$(wildcard $(BIBDIR)/*.bib)
ifneq ("$(BIBFILE)","")
BIBTEX = --biblatex --bibliography=report.bib
report.bib: $(BIBFILE)
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml *.bib
	cat $(BIBDIR)/*.bib > $@  
else
BIBTEX =
endif

# Generate PDF from TIKZ
%.pdf: %.tikz
	FILE=$(notdir $<)
	cd $(dir $<); \
	pdflatex $(notdir $<); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk
	@echo $<

# Generate PDF with TEX from SVG
%.pdf: %.svg
	inkscape -D -z --file=$< --export-pdf=$@ --export-latex

%.png: %.svg
	inkscape -D -z --file=$< --export-png=$@
	
# Generate TEX
%.tex: $(SOURCE)/%.md
	# Debugging
	pandoc $< $(PANDOC_OPTS) -V debug -o $@

# Cat md files into one
report.md: $(MD)
	cat $(SOURCE)/*.md > $@

# Generate TEX
report.tex: report.md $(TEMPLATE) $(YAML) bib
	# Generating report
	pandoc $< $(YAML) $(PANDOC_OPTS) $(BIBTEX) -o $@

%.pdf: %.tex figures
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	latexmk -pdf -pv -pdflatex="$(LATEX) $(LATEXOPT) $(NONSTOP) %O %S" $<
	
clean:
	latexmk -C
	rm -f *.pdfsync
	rm -rf *~ *.tmp
	rm -f $(TEX) report.tex report.md *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml *.bib
	
cleanfig:
	rm -f $(PDF_SVG) $(PDF_TEX) $(PNG_SVG) $(TIKZPDF)

rebuild: clean all
