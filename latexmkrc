# mathmodel-skill latexmk build config.
# Canonical copy lives at the repository root; a mirror ships with the
# latex-alt CUMCM fallback class at templates/latex-alt/cumcm/latexmkrc.
# Keep them in sync (guarded by tests/test_mirror_parity.py).

$pdf_mode = 5;
$xelatex = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';

# BibTeX command fallback. Some minimal Linux images expose bibtex.original
# while the /usr/bin/bibtex alternative is broken or absent.
if (system('command -v bibtex >/dev/null 2>&1 && bibtex --version >/dev/null 2>&1') == 0) {
  $bibtex = 'bibtex %O %B';
} elsif (system('command -v bibtex.original >/dev/null 2>&1') == 0) {
  $bibtex = 'bibtex.original %O %B';
} elsif (system('command -v bibtex8 >/dev/null 2>&1') == 0) {
  $bibtex = 'bibtex8 %O %B';
} else {
  $bibtex = 'bibtex %O %B';
}
$biber = 'biber %O %B';
$max_repeat = 5;

push @generated_exts, 'synctex.gz';
