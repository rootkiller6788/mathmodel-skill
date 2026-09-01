% Lightweight CUMCMThesis-compatible class for mathmodel-skill.
% This file is intentionally self-contained and does not embed or require
% proprietary font files. It implements the common cumcmthesis commands used by
% the bundled CUMCM electronic-paper template. For strict matching to another
% third-party CUMCMThesis template, replace this file with that template's
% cumcmthesis.cls and follow its license and font requirements.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cumcmthesis}[2026/06/30 v1.0.8 lightweight CUMCM electronic-paper compatibility class]

\newif\if@mcm@bwprint
\@mcm@bwprintfalse
\newif\if@mcm@preface
\@mcm@prefacetrue

\DeclareOption{colorprint}{\@mcm@bwprintfalse}
\DeclareOption{bwprint}{\@mcm@bwprinttrue}
\DeclareOption{withoutpreface}{\@mcm@prefacefalse}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexart}}
\ExecuteOptions{colorprint}
\ProcessOptions\relax

\LoadClass[UTF8,a4paper,zihao=-4]{ctexart}

\RequirePackage[margin=2.5cm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{setspace}
\RequirePackage{etoolbox}
\RequirePackage{hyperref}

\hypersetup{colorlinks=true,allcolors=black,breaklinks=true}
\pagestyle{fancy}
\fancyhf{}
\cfoot{\thepage}
\renewcommand{\headrulewidth}{0pt}
\setlength\parindent{2em}

% Token commands kept for compatibility with common cumcmthesis templates.
\newcommand*{\mcm@tokens@tihao}{}
\newcommand*{\mcm@tokens@baominghao}{}
\newcommand*{\mcm@tokens@schoolname}{}
\newcommand*{\mcm@tokens@membera}{}
\newcommand*{\mcm@tokens@memberb}{}
\newcommand*{\mcm@tokens@memberc}{}
\newcommand*{\mcm@tokens@supervisor}{}
\newcommand*{\mcm@tokens@yearinput}{}
\newcommand*{\mcm@tokens@monthinput}{}
\newcommand*{\mcm@tokens@dayinput}{}

\newcommand*{\tihao}[1]{\renewcommand*{\mcm@tokens@tihao}{#1}}
\newcommand*{\baominghao}[1]{\renewcommand*{\mcm@tokens@baominghao}{#1}}
\newcommand*{\schoolname}[1]{\renewcommand*{\mcm@tokens@schoolname}{#1}}
\newcommand*{\membera}[1]{\renewcommand*{\mcm@tokens@membera}{#1}}
\newcommand*{\memberb}[1]{\renewcommand*{\mcm@tokens@memberb}{#1}}
\newcommand*{\memberc}[1]{\renewcommand*{\mcm@tokens@memberc}{#1}}
\newcommand*{\supervisor}[1]{\renewcommand*{\mcm@tokens@supervisor}{#1}}
\newcommand*{\yearinput}[1]{\renewcommand*{\mcm@tokens@yearinput}{#1}}
\newcommand*{\monthinput}[1]{\renewcommand*{\mcm@tokens@monthinput}{#1}}
\newcommand*{\dayinput}[1]{\renewcommand*{\mcm@tokens@dayinput}{#1}}

\newcommand*{\mcm@printpreface}{%
  \thispagestyle{empty}%
  \begin{center}
    {\heiti\zihao{3} 高教社杯全国大学生数学建模竞赛承诺书占位页\par}
    \vspace{2em}
    {\zihao{-4} 本页仅作为本地草稿占位。正式纸质提交请使用当年官方承诺书专用页。\par}
  \end{center}
  \newpage
  \thispagestyle{empty}%
  \begin{center}
    {\heiti\zihao{3} 编号专用页占位页\par}
    \vspace{2em}
    {\zihao{-4} 本页仅作为本地草稿占位。正式纸质提交请使用当年官方编号专用页。\par}
  \end{center}
  \newpage
}

\renewcommand{\maketitle}{%
  \par\begingroup
  \if@mcm@preface
    \mcm@printpreface
  \fi
  \setcounter{page}{1}%
  \thispagestyle{fancy}%
  \begin{center}
    {\heiti\zihao{2}\@title\par}%
  \end{center}
  \vspace{1.5em}
  \endgroup
}

\renewenvironment{abstract}{%
  \par\begingroup
  \thispagestyle{fancy}%
  \begin{center}
    {\heiti\zihao{3} 摘要\par}%
  \end{center}
  \vspace{1em}%
  \setlength{\parindent}{2em}%
}{%
  \par\endgroup\newpage
}

\newcommand{\keywords}[1]{%
  \par\vspace{1em}\noindent{\heiti 关键词：}#1\par
}

\endinput
