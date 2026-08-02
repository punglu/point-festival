# REV-FAIL-2026-08-02-boxsizing

Superseded A2 revision, retained deliberately as the record of a real defect
found by the evidence harness rather than by inspection.

```text
Verdict            : FAIL
Cause              : box-sizing mismatch between canonical and implementation
Canonical source   : declares box-sizing 0 times -> browser default content-box
Implementation     : inherited `* { box-sizing: border-box }` from reset.css
Measured symptom   : hero height canonical 226 vs implementation 196 (-30)
                     every zone below the hero offset by exactly -30
                     30 == the hero's 15px top + 15px bottom padding
Unaffected         : every other zone matched at 0.00px in x/width/height
Pixel diff         : 33.88% / 31.98% / 27.61% at 375 / 390 / 430
Fix                : scope `box-sizing: content-box` to the preview subtree so
                     each canonical literal means what it means in canonical
```

Superseded by `final/`. Do not compare these PNGs against the current
implementation.
