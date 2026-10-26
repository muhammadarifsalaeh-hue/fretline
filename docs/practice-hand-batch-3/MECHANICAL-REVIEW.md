# Independent mechanical integration review — Batch 3

This review changed no runtime source, chord, model, test threshold or approval flag. It independently read the completed full-library audit, the actual runtime JSON, the integration helper, the per-candidate source evidence, and the preservation and musical-check reports.

## Completed checks

- The final all-42 report binds the current library SHA-256, unchanged musical source hash and unchanged actual GLB hash. Every row's root/local-bone transform hash was independently recomputed from the integrated runtime record.
- Exactly **7 of 42** endpoints pass actual geometry: C, Cmaj7, Am7, Em7, E7, Fmaj7 and Dm. The full required-batch test has no errors. The other **35 are rejected**, not counted as passed or visually approved.
- Accepted endpoints have zero combined skin/sleeve self crossing pairs, zero exact runtime guitar crossing pairs, no dense wood samples beyond the unchanged 0.02 mm threshold, valid assigned-owner palmar contacts in the correct string/fret region, and all open strings above the unchanged 0.2 mm clearance threshold.
- Correct contacts are evaluated using unchanged central musical data, rather than trusting a pose's authored target labels. Barre and fingertip ownership have separate checks. No musical voicing, string/fret position or finger assignment was changed to fit a hand.
- The four integrated source candidates and their transforms match genuine passing candidate audits. The integration helper verifies model/music/transform binding, self and guitar results, wood, contacts and open strings before it sets only the geometric contact/collision flags.
- Exactly four runtime records differ from `74c2076`: Em7, E7, Fmaj7 and Dm. The other 38 pose records, including C/Cmaj7/Am7, are unchanged. All 42 remain `needs-review`, `reviewed: false`, `anatomyPassed: false`, and `multiViewReviewed: false`.
- Fresh independent music/fingering checks actually completed **86/86**. This supports the table's musical-data pass column; visual/browser diagram checks remain a separate QA result.
- The recorded preservation checks confirm the same 197 protected site files and four music/model/metadata/rig files remain byte-for-byte unchanged.

## Rejected authoring work is separate

D and G experiments removed their self intersections but still failed actual guitar/wood/contact tests. Dsus2, Em, Am, F and C7 experiments likewise did not satisfy every gate. These are retained as rejection evidence only. Their improved intermediate metrics cannot replace the integrated runtime results in the 42-row table. The initial rejected Dm trials are also retained, followed by the separately bound final surgical pass.

The final Dm success moves the ring contact 2 mm toward the nut inside the original legal fret region, and refines the actual index palmar surface. Fmaj7 refines the ring contact without changing the root/wrist or unrelated digits. Em7/E7 use a pinned source seed; E7 preserves the existing middle-finger contact. The successful operations use saved real rig rotations and skin surfaces, rather than a chord-name substitution or a static image.

## Remaining limits

A mechanical endpoint pass is not anatomical or teaching approval. The hand's proximal curl, overall natural presentation and finite cropped forearm/sleeve remain review issues. Existing source weights are normalized; this does not prove deep skin folding or all muscle/joint posture is anatomically correct. The source rig/model was preserved, rather than globally rewriting weights without local evidence.

The gate is a strong rejection check, not an exhaustive continuum proof: dense wood sampling is finite, triangle crossings do not certify every possible fully enclosed solid overlap, and no swept bone path between accepted poses has been approved. The separate bounded appearance reveal does not interpolate the rig and does not claim realistic physical chord-changing motion.

This review performed no new browser rendering or physical iPad Safari test. Chromium/Linux WebKit results and actual screenshots belong to the completed browser QA report; Linux WebKit alone cannot approve real iPad Safari performance. **Verified teaching hands remain 0/42.**
