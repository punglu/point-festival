# A2 comparison contract — read before quoting any number

Two comparisons exist here. **They must never be mixed or averaged.**

## PRIMARY — fidelity gate (`primary-png-comparison/`)

```text
base       : approved PNG, native content bounds, CROP ONLY (no resize/stretch/warp)
             screen_family_home_approved.png  sha256 d486d0eb...70e9f2
             app-content crop (0,83,941,1558) — status bar and home indicator excluded
scale      : deviceScaleFactor 2.0, CSS viewport 470x779
             fitted by least squares over PNG landmark heights, assuming no HTML value
             (fit 1.9961; rms 9.44 vs 10.12 @1.9604, 10.17 @2.05, 23.20 @2.2951)
             => approved PNG is a 2x export of a ~470.5 x 836 CSS design canvas
authority  : approved PNG is visual-final
```

**This is the only comparison that speaks to canonical visual fidelity.**

## SECONDARY — responsive regression (`canonical/ implementation/ side-by-side/ diff/ overlay/`)

```text
base       : canonical HTML 1b rendered per viewport
viewports  : 375x812, 390x844, 430x932
purpose    : responsive behaviour only — overflow, wrapping, truncation, rhythm
             consistency across widths
```

The canonical-HTML diff percentage here is **expected to be large and is not a
defect**: the implementation deliberately departs from the canonical HTML on two
points where the approved PNG overrides it —

1. `D-A2-1` the 우리 서비스 card wrapper, present in the PNG, absent from the HTML
2. the hero height, PNG 417 PNG px (208.5 CSS) vs the HTML's 196 content-box (226 CSS)

Quoting the secondary diff percentage as approved-PNG fidelity is a category
error. Quoting the earlier `0.00px canonical-HTML parity` as canonical visual
parity was the same error, and is retracted.
