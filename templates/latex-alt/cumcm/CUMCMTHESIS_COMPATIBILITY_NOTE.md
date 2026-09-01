# cumcmthesis compatibility note

This skill includes a lightweight `cumcmthesis.cls` compatibility file so that
`templates/cumcm/main.tex` can compile out of the box with XeLaTeX.

It is not a verbatim copy of the common third-party CUMCMThesis template. The
public `latexstudio/CUMCMThesis` repository has a `cumcmthesis.cls`, but the
repository page does not expose a clear redistribution license at the time this
skill was packaged, and its common variants may require local Chinese font files.
To keep this skill redistributable and portable, this compatibility class uses
`ctexart`, `geometry`, and `fancyhdr`, and it does not bundle font files.

For a competition submission, official contest documents always override this
compatibility class. If you intentionally use another `cumcmthesis.cls`, place it
beside your `main.tex` or install it in your TeX tree, and verify its license,
font requirements, page numbering, anonymous submission behavior, and current
year compliance.
