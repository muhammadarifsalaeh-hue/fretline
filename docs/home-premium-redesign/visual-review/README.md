# Independent Homepage visual and accessibility review

Read-only Chromium review against the development source on port 5454, at 1440×1000, 768×1024, 390×844 and 320×740. This is separate from the production browser acceptance suite.

Actual result: **20/20 region/viewport checks passed**, with zero console/runtime errors. Reviewed Hero, brand rail, categories, inline Quiz and comparison. Visible headings, descriptions, option labels and model names have no internal horizontal text overflow. The document stays within each viewport. All visible primary buttons meet a 44×44px target; all visible images decoded successfully.

The initial general text probe incorrectly included intentionally clipped `.sr-only` headings and progress announcements. The replay script explicitly excludes that accessibility-only class from visible-text overflow checks. No application styling or expectation was relaxed to accommodate a real text overflow.

The root specificity correction is effective: category cards show two columns at 768px, with complete contained instruments. The dark/gold hierarchy, selected controls and pictured choices match the intended structure. Exact source photos have original background differences from the references; selected comparison models remain the actual registered Yamaha FG820-12 and Martin D-28, both acoustic, rather than borrowing an electric product image.

The existing Featured collection still contains catalog entries without registered publication photographs. This review does not claim those gaps were filled. The brand rail has nine actual logo files and honest Córdoba typography; no permitted tenth standalone logo was invented.

## Tall element screenshot artifact

Playwright long-element captures may render fixed navigation and translated skip links at stitched positions that differ from the actual viewport. The independently captured `narrow-find-viewport.png` confirms the skip link is offscreen and unfocused during ordinary touch scrolling: top −83.03px, bottom −30.24px, transform translateY(−95.03px), active element `main`, neither `:focus` nor `:focus-visible`. No skip-link source change is necessary. Prefer actual viewport screenshots when assessing fixed-navigation overlaps.

This is not a formal WCAG certification or a physical iPad Safari test. Linux browser and synthetic touch results cannot establish physical-device behavior. Source files were not changed by this review.
