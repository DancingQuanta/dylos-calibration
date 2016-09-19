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
\graphicspath{../imgs}
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

\newcolumntype{M}{>{\centering\arraybackslash}m{0.45\textwidth}}
\newcolumntype{C}{>{\centering\arraybackslash}m{0.2\textwidth}}

\title{\VAR{output['title']}}
\author{\VAR{output['author']}}

\BLOCK{set calibratee = sensors['calibratee']}
\BLOCK{set calibrater = sensors['calibrater']}
\BLOCK{set rebinned = sensors['rebinned']}

\begin{document}
\maketitle
This summary report showing the calibration of \VAR{calibratee['name']} by \VAR{calibrater['name']}.
Each of these sensors have different properties such as air flow air and particle concentration units.
All data produced will be converted from their respective units to \VAR{output['unit']}.

\begin{center}
\begin{tabular}{m{0.3\textwidth}CC}
& \VAR{calibrater['name']} & \VAR{calibratee['name']} \\
Number of size channels & 
\VAR{calibrater['bins']['stringbins']|length} &
\VAR{calibratee['bins']['stringbins']|length} \\
Channels &
\VAR{calibrater['bins']['stringbins']|join} &
\VAR{calibratee['bins']['stringbins']|join} \\
Input unit & 
\VAR{calibrater['unit']} &
\VAR{calibratee['unit']} \\
Concentration &
\VAR{calibrater['concentration']} &
\VAR{calibratee['concentration']} \\
Flow rate &
\VAR{calibrater['flowrate']} &
\VAR{calibratee['flowrate']} \\
Count rate &
\VAR{calibrater['count rate']} &
\VAR{calibratee['count rate']} \\

Scale factor of input unit to \VAR{output['unit']} &
\VAR{calibrater['scale factor']} &
\VAR{calibratee['scale factor']} \\
\end{tabular}
\end{center}

\clearpage
\BLOCK{for item in exp['order']}
\BLOCK{set condition = exp['conditions'][item]['results']}

\section{\VAR{item}}
\subsection{\VAR{calibrater['name']}}
\begin{tabular}{MM}
\input{\VAR{condition['calibrater']['plot']}} &
\input{\VAR{condition['calibration']['plot']}} \\
\end{tabular}
\begin{tabular}{MM}
\input{\VAR{condition['calibrater']['histogram']['histplot']['hist']}} &
\input{\VAR{condition['calibrater']['histogram']['histplot']['histlog']}} \\
\end{tabular}
\begin{tabular}{MM}
\input{\VAR{condition['calibrater']['histogram']['histdata']}} &
\input{\VAR{condition['calibrater']['histogram']['histstats']}} \\
\end{tabular}

\subsection{\VAR{calibratee['name']}}
\begin{tabular}{MM}
\input{\VAR{condition['calibratee']['histogram']['histplot']['hist']}} &
\input{\VAR{condition['calibratee']['histogram']['histplot']['histlog']}} \\
\end{tabular}
\begin{tabular}{MM}
\input{\VAR{condition['calibratee']['histogram']['histdata']}} &
\input{\VAR{condition['calibratee']['histogram']['histstats']}} \\
\end{tabular}

\subsection{\VAR{rebinned['name']}}
\begin{tabular}{MM}
\input{\VAR{condition['rebinned']['histogram']['histplot']['hist']}} &
\input{\VAR{condition['rebinned']['histogram']['histplot']['histlog']}} \\
\end{tabular}
\begin{tabular}{MM}
\input{\VAR{condition['rebinned']['histogram']['histdata']}} &
\input{\VAR{condition['rebinned']['histogram']['histstats']}} \\
\end{tabular}

\subsection{Calibration curve}
\input{\VAR{condition['calibration']['regression']['scatter']}}

\clearpage
\BLOCK{endfor}

\section{Calibration parameters}

\input{\VAR{exp['calibration']}}

\end{document}
