\RequirePackage[l2tabu, orthodox]{nag}
\documentclass[11pt,a4paper]{article} % a4 dimension 210X297mm 21x29.7cm 595.3x841.9pts

\usepackage[margin=2cm]{geometry} % 56.69 pts
\usepackage[english]{babel} % English language/hyphenation

\usepackage[T1]{fontenc}
\usepackage[utf8x]{inputenc}
\usepackage[mono=false]{libertine}
\usepackage[scaled=0.85]{beramono}%% or 0.82
\usepackage{verbatim}
\usepackage[protrusion=true,expansion=true]{microtype}
\UseMicrotypeSet[protrusion]{basicmath} % disable protrusion for tt fonts
\usepackage{amssymb,amsfonts,amsthm} % Math packages
\usepackage[libertine]{newtxmath}
\usepackage[separate-uncertainty=false,multi-part-units=single]{siunitx}
\usepackage{gensymb}
\usepackage{mathtools}
\usepackage{cancel}
\usepackage[table]{xcolor}
\usepackage[font=small,skip=0pt,labelfont=bf,textfont=it,up]{caption}
\usepackage{framed}

\usepackage[pdftex]{graphicx}
\graphicspath{../../imgs}
\usepackage{subcaption}
\usepackage{epstopdf}
\epstopdfDeclareGraphicsRule{.gif}{png}{.png}{convert gif:#1 png:\OutputFile}
\AppendGraphicsExtensions{.gif}
\makeatletter
\def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
\def\maxheight{\ifdim\Gin@nat@height>\textheight\textheight\else\Gin@nat@height\fi}
\makeatother
% Scale images if necessary, so that they will not overflow the page
% margins by default, and it is still possible to overwrite the defaults
% using explicit options in \includegraphics[width, height, ...]{}
\setkeys{Gin}{width=\maxwidth,height=\maxheight,keepaspectratio}

\usepackage{longtable,booktabs,multirow,array}
\usepackage{pgfplotstable}
\pgfplotsset{compat=1.12}

\usepackage{float}
\usepackage{csquotes}
\usepackage{import}% For the pdf_tex as the pdf_tex reference to another file
\usepackage{physics}
\usepackage{myphysics}
\usepackage{mychem}
\usepackage{chemfig}
\usepackage[version=4]{mhchem}

\setlength{\parindent}{1em}
\setlength{\parskip}{6pt plus 2pt minus 1pt}
\setlength{\emergencystretch}{3em}  % prevent overfull lines
\providecommand{\tightlist}{%
	\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\usepackage{showframe}

\begin{document}
\fbox{\input{\VAR{plots['hist-mat']}}}
\end{document}
