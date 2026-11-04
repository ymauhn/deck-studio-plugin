% Instituto de Computação - Unicamp
% LaTeX document class for theses and dissertations.
% ic-tese-v3 2025-0505

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ic-tese-v3}[]
\typeout{ic-tese-v3}

\def\thesislanguage#1{\gdef\@thesislanguage{#1}}
\DeclareOption{Ingles}{
  \thesislanguage{0}
  \typeout{ic-tese: ingles.}
}
\DeclareOption{Espanhol}{
  \thesislanguage{1}
  \typeout{ic-tese: espanhol.}
}
\DeclareOption{Portugues}{
  \thesislanguage{2}
  \typeout{ic-tese: portugues.}
}
\newif\iffinalversion
\DeclareOption{Final}{
  \finalversiontrue
  \typeout{ic-tese: versao final.}
}


\ProcessOptions\relax

\LoadClass[12pt,a4paper]{report}

\ifcase\@thesislanguage
\RequirePackage[english,brazil]{babel}
\or
\RequirePackage[english,spanish,brazil]{babel}
\or
\RequirePackage[english,brazil]{babel}
\fi

\usepackage[T1]{fontenc}
\RequirePackage{graphicx}
\PassOptionsToPackage{table}{xcolor}
\RequirePackage{pdfpages}
\RequirePackage{xspace}

\RequirePackage{setspace}
\RequirePackage{geometry}
\geometry{a4paper,top=30mm,bottom=20mm,left=30mm,right=20mm}

\RequirePackage[titletoc]{appendix}

\usepackage[absolute]{textpos}

\RequirePackage{fancyhdr}

\gdef\@UNICAMP{Universidade Estadual de Campinas}


% User fields:
\gdef\@unidadept{Instituto de Computação}
\def\unidadept#1{\gdef\@unidadept{#1}}

\gdef\@unidadeen{Institute of Computing}
\def\unidadeen#1{\gdef\@unidadeen{#1}}

\gdef\@sigla{IC}
\def\sigla#1{\gdef\@sigla{#1}}

\gdef\@programa{Programa de Pós-Graduação em Ciência da Computação}
\def\programa#1{\gdef\@programa{#1}}

\let\@autor\relax
\def\autor#1{\gdef\@autor{#1}}
\author{\@autor}

\let\@autora\relax
\def\autora#1{\gdef\@autora{#1}}

\let\@titulo\relax
\def\titulo#1{\gdef\@titulo{#1}}

\gdef\@cursopt{Ci\^encia da Computa\c{c}\~ao}
\def\cursopt#1{\gdef\@cursopt{#1}}

\gdef\@cursoen{Computer Science}
\def\cursoen#1{\gdef\@cursoen{#1}}

\gdef\@cursoes{Ciencia de la Computaci\'on}
\def\cursoes#1{\gdef\@cursoes{#1}}

\newif\ifmaster

\gdef\mestrado{
  \if\@autora\relax
  \gdef\@degnamept{Mestre}
  \gdef\@degnamees{Maestro}
  \else
  \gdef\@degnamept{Mestra}
  \gdef\@degnamees{Maestra}
  \fi
  \gdef\@degnameen{Master}
  \gdef\@monopt{Disserta\c{c}\~ao}
  \gdef\@monoes{Dissertac\'ion}
  \gdef\@monoen{Dissertation}
}
\gdef\doutorado{
  \if\@autora\relax
  \gdef\@degnamept{Doutor}
  \gdef\@degnamees{Doctor}
  \else
  \gdef\@degnamept{Doutora}
  \gdef\@degnamees{Doctora}
  \fi
  \gdef\@degnameen{Doctor}
  \gdef\@monopt{Tese}
  \gdef\@monoes{Tesis}
  \gdef\@monoen{Thesis}
}

\let\@orientador\relax
\def\orientador#1{\gdef\@orientador{#1}}

\let\@orientadora\relax
\def\orientadora#1{\gdef\@orientadora{#1}}

\gdef\@advisors{1}
\let\@coorientador\relax
\def\coorientador#1{\gdef\@coorientador{#1}\gdef\@advisors{2}}

\let\@coorientadora\relax
\def\coorientadora#1{\gdef\@coorientadora{#1}\gdef\@advisors{2}}

\def\datadadefesa#1#2#3{
  \gdef\@dia{#1}
  \gdef\@mes{#2}
  \gdef\@ano{#3}
}

\let\@fichacatalografica\relax
\def\fichacatalografica#1{\gdef\@fichacatalografica{#1}}

\let\@avalA\relax
\let\@avalB\relax
\let\@avalC\relax
\let\@avalD\relax
\let\@avalE\relax
\let\@avalF\relax
\let\@avalG\relax
\let\@avalH\relax
\let\@instavalA\relax
\let\@instavalB\relax
\let\@instavalC\relax
\let\@instavalD\relax
\let\@instavalE\relax
\let\@instavalF\relax
\let\@instavalG\relax
\let\@instavalH\relax

\def\avaliadorA#1#2{\gdef\@avalA{#1}\gdef\@instavalA{#2}}
\def\avaliadorB#1#2{\gdef\@avalB{#1}\gdef\@instavalB{#2}}
\def\avaliadorC#1#2{\gdef\@avalC{#1}\gdef\@instavalC{#2}}
\def\avaliadorD#1#2{\gdef\@avalD{#1}\gdef\@instavalD{#2}}
\def\avaliadorE#1#2{\gdef\@avalE{#1}\gdef\@instavalE{#2}}
\def\avaliadorF#1#2{\gdef\@avalF{#1}\gdef\@instavalF{#2}}
\def\avaliadorG#1#2{\gdef\@avalG{#1}\gdef\@instavalG{#2}}
\def\avaliadorH#1#2{\gdef\@avalH{#1}\gdef\@instavalH{#2}}

\let\@cotutela\relax
\def\cotutela#1{\gdef\@cotutela{#1}}


\def\paginasiniciais{
  \newlength{\oldparindent}
  \setlength{\oldparindent}{\parindent}
  \setlength\parindent{0pt}
  \thispagestyle{empty}
  \pagestyle{empty}
  \makeatletter
  \let\ps@mystyle\ps@plain
  \let\ps@plain\ps@empty
  \makeatother
  \openningpage
  \clearpage
  \titlepage
  \clearpage
  \cathpage
  \clearpage
  \approvalpage
  \clearpage
  \setlength{\parindent}{\oldparindent}
  \resetlang
}


\def\logos{
  \noindent
  \raisebox{-.5\height}{\includegraphics[width=2.2cm]{logo-unicamp.eps}}
}


\def\openningpage{
  \logos
  \vskip 20mm
  \noindent
  \begin{center}
    \textbf{\@UNICAMP\ (UNICAMP)} \\
    \vskip 2mm
    \textbf{\@unidadept\xspace(\@sigla)} \\
    \vskip 2mm
    \textbf{\@programa}
  \end{center}
  \vskip 20mm
  \begin{center}
    {\bf \if\@autora\relax\@autor\else\@autora\fi}
    \vskip 20mm
    \ifcase\@thesislanguage
      {\bf\@title}
      \vskip 20mm
    \or
      {\bf\@title}
      \vskip 20mm
    \fi
    {\bf \@titulo}
    \vskip 50mm
    \vfill
    CAMPINAS\\
    \@ano
    \vspace*{10mm}
  \end{center}
}


\def\titlepage{
  \bf
  \vspace*{30mm}
  \begin{center}
    \if\@autora\relax\@autor\else\@autora\fi
    \vskip 3mm
    \ifcase\@thesislanguage
      \@title
      \vskip 3mm
    \or
      \@title
      \vskip 3mm
    \fi
    \@titulo
  \end{center}
  \vskip 22mm
  \normalfont
  \normalsize
  \hfill\begin{minipage}[t]{0.54\textwidth}
    \supresshyphen
    \@monopt\xspace apresentada ao \@unidadept\xspace da
    \@UNICAMP\xspace(UNICAMP) como parte dos requisitos exigidos
    para a obten\c{c}\~ao do t\'{\i}tulo de \@degnamept\xspace em
    \@cursopt\xspace
    \ifx\@cotutela\relax\else
      no \^ambito do acordo  de Cotutela firmado entre a Unicamp e a \@cotutela
    \fi.
  \end{minipage}
 
  \vskip 8mm

  \ifcase\@thesislanguage
      
  \hfill\begin{minipage}[t]{0.54\textwidth}
  \supresshyphen
  \@monoen\xspace presented to the \@unidadeen\xspace of the
  University of Campinas (UNICAMP) in partial fulfillment of the
  requirements for the degree of \@degnameen\xspace in
  \@cursoen\xspace
  \ifx\@cotutela\relax\else
    under the double-diploma agreement between Unicamp and \@cotutela
  \fi.
  \end{minipage}
   \else
    \vspace{10mm}
    \fi

  
  \vskip 30mm
  \if\@orientadora\relax {\bf Orientador: \@orientador}
  \else {\bf Orientadora: \@orientadora}
  \fi
  \ifnum\@advisors=2
    \\
    \if\@coorientadora\relax {\bf Coorientadores: \@coorientador}
    \else {\bf Coorientadora: \@coorientadora}
    \fi
  \fi
  \vskip 15mm
  \iffinalversion
    Este exemplar corresponde \`{a} vers\~{a}o final da
    \lowercase\expandafter{\@monopt}\xspace defendida.
  \else
    Este exemplar corresponde \`{a} vers\~{a}o da
    \lowercase\expandafter{\@monopt}\xspace entregue \`{a} banca
    antes da defesa.
  \fi
}


\def\cathpage{
  \ifx\@fichacatalografica\relax
  Na vers\~ao final esta p\'agina ser\'a substitu\'{\i}da pela
  ficha catalogr{\'a}fica. \\\\
  De acordo com o padr\~ao da CCPG: ``Quando se tratar de Teses e
  Disserta\c{c}\~oes financiadas por ag\^encias de fomento, os beneficiados
  dever\~ao inserir no formul\'ario de solicita\c{c}\~ao da ficha
  catalogr\'afica as informa\c{c}\~oes sobre ag\^encia e  n\'umero do processo
  pelo qual receberam o aux\'{\i}lio, por\'em essa informa\c{c}\~ao n\~ao
  ficar\'a vis\'ivel na ficha, ser\'a utilizada para fins estat\'isticos. Os
  aux\'ilios recebidos devem tamb\'em ser citados na se\c{c}\~ao
  ``Agradecimento'' seguindo os padr\~oes exigidos pelas ag\^encias de
  fomento.''\\e\\``caso a tese de doutorado seja feita em Cotutela,
  ser\'a necess\'ario informar na ficha catalogr\'afica o fato, a Universidade
  convenente, o pa\'{\i}s e o nome do orientador.''
  \else
  \includepdf[pagecommand={}]{\@fichacatalografica}
  \fi
}


\def\approvalpage{
  \iffinalversion
    \prefacesection{\ } % Folha de aprovação
    \vskip 5mm
    \begin{center}
      {\bf \if\@autora\relax\@autor\else\@autora\fi}
    \end{center}
    \vskip 15mm
    \supresshyphen
    \@monopt\xspace apresentada ao \@programa, defendida na data de \@dia/\@mes/\@ano.
    \vskip 20mm
    Composição da Comiss\~ao Examinadora:
    \vskip 7mm
    \ifx\@avalA\relax
    \else
      \begin{list}{}{\setlength{\itemindent}{0pt}\setlength{\leftmargin}{0pt}}
        %remover indentacao
        \item \@avalA\newline\@instavalA
        \ifx\@avalB\relax\else \item \@avalB\newline\@instavalB\fi
        \ifx\@avalC\relax\else \item \@avalC\newline\@instavalC\fi
        \ifx\@avalD\relax\else \item \@avalD\newline\@instavalD\fi
        \ifx\@avalE\relax\else \item \@avalE\newline\@instavalE\fi
        \ifx\@avalF\relax\else \item \@avalF\newline\@instavalF\fi
      \end{list}
    \fi
    \vfill
  \else
    Na vers\~ao final, esta p\'agina ser\'a substitu\'{\i}da por outra
    informando a data da defesa e a composi\c{c}\~ao da banca.
  \fi
}


\newcommand\ourchapter{\if@openright\cleardoublepage\else\clearpage\fi
                    \thispagestyle{plain}%
                    \global\@topnum\z@
                    \@afterindentfalse
                    \@ourchapter}

\def\@ourchapter#1{%
  \if@twocolumn
    \@topnewpage[\@makeschapterhead{#1}]%
  \else
    \@ourmakechapterhead{#1}%
    \@afterheading
  \fi
}

\def\@ourmakechapterhead#1{%
  %\vspace*{50\p@}%
  {\parindent \z@ \raggedright
    \normalfont
    \interlinepenalty\@M
    \Huge \bfseries  #1\par\nobreak
    \vskip 40\p@
  }}

\renewcommand\listoffigures{%
    \ourchapter{\listfigurename}%
      \@mkboth{\MakeUppercase\listfigurename}%
              {\MakeUppercase\listfigurename}%
    \@starttoc{lof}%
    }

\renewcommand\listoftables{%
    \ourchapter{\listtablename}%
      \@mkboth{%
          \MakeUppercase\listtablename}%
         {\MakeUppercase\listtablename}%
    \@starttoc{lot}%
    }



\def\prefacesection#1{
\ifx\#1\relax
  \relax
  \else
  \ourchapter{#1}
  \fi
  \pagestyle{empty}
  \thispagestyle{empty}
}


\gdef\resetlang{
  \ifcase\@thesislanguage\relax
  \selectlanguage{english}
  \or\selectlanguage{spanish}
  \or\selectlanguage{brazil}
  \fi
}


\gdef\supresshyphen{
  \tolerance=1
  \emergencystretch=\maxdimen
  \hyphenpenalty=10000
  \hbadness=10000
}


\newenvironment{resumo}{\prefacesection{Resumo}\selectlanguage{brazil}}{\resetlang \newpage}
\renewenvironment{abstract}{\prefacesection{Abstract}\selectlanguage{english}}{\resetlang \newpage}
\newenvironment{resumen}{\prefacesection{Resumen}\selectlanguage{spanish}}{\resetlang \newpage}


\newenvironment{epigrafe}
{\newpage\mbox{}\vfill\hfill\begin{minipage}[t]{0.5\textwidth}\supresshyphen}
{\end{minipage}\newpage}


\newcommand{\fimdaspaginasiniciais}{
\newpage
\makeatletter
\let\ps@plain\ps@mystyle
\makeatother
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\setlength{\headheight}{14.5pt}
\fancyhead[R]{\thepage}
\fancypagestyle{plain}{\fancyhf{}\fancyhead[R]{\thepage}}
\setstretch{1.1}
}

\addtocontents{toc}{\protect\enlargethispage{-35mm}}

\let\@oldbiblio\thebibliography
\renewcommand{\thebibliography}[1]{\newpage\addcontentsline{toc}{chapter}{\bibname}\@oldbiblio{#1}}
