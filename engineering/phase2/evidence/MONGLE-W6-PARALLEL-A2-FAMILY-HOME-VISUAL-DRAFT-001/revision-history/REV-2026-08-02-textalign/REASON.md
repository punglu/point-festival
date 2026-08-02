# REV-2026-08-02-textalign

Superseded A2 revision. Geometry was already exact; this revision isolates the
text-alignment defect.

```text
Verdict     : SUPERSEDED
Residual    : 3.82% / 3.45% / 3.10% at 375 / 390 / 430
Cause 1     : `.tile { text-align: center }` — an implementation invention with
              no canonical basis. Canonical inherits `text-align: start`.
Cause 2     : this preview uses real <button>s for affordances; the UA stylesheet
              gives buttons `text-align: center`, which the canonical <div>-based
              source never had. Every wrapped tile sublabel was recentred.
Proof       : per-element probe reported textAlign start->center on all four tile
              sublabels, all four tile labels and all four dock labels.
Fix         : removed the invented rule; added `.page button { text-align: start }`.
Also        : `text-rendering: auto` was added in this revision on suspicion, and
              measured to change nothing on these fonts in Chromium. It is kept
              because it restores the canonical value, but it is recorded here as
              a corrected mis-attribution, not as the fix.
```

Superseded by `final/`.
