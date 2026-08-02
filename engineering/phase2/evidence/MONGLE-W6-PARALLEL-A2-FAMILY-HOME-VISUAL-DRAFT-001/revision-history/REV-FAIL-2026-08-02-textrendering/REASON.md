# REV-FAIL-2026-08-02-textrendering

Superseded A2 revision. Geometry was already exact here; this revision is kept
because it isolates a second, purely typographic defect.

```text
Verdict          : SUPERSEDED (geometry PASS, raster FAIL)
Geometry         : every zone matched at 0.00px after the box-sizing fix
Residual diff    : 3.82% / 3.45% / 3.10% at 375 / 390 / 430
Concentration    : text rows only (activity band mean 17.11 vs empty band 0.00)
Cause            : global.css sets `text-rendering: optimizeLegibility` on body;
                   the canonical source leaves it at `auto`. The property changes
                   kerning/ligature shaping, moving glyphs sub-pixel.
Proof            : computed-style probe of the same element on both sides
                   reported exactly one differing property — textRendering.
Fix              : `text-rendering: auto` scoped to the preview subtree.
Also fixed here  : diff PNGs were written from an RGBA difference, whose alpha
                   channel is 0 everywhere, making every saved diff render fully
                   transparent and unreadable. Now written from RGB, plus an
                   8x amplified companion.
```

Superseded by `final/`.
