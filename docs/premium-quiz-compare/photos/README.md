# Discovery photography — actual acquisition and license review

Five existing real photographs were selected for the Quiz and Compare redesign. They are **generic editorial atmosphere**, never proof of the model, finish, specification, price or endorsement of a selected catalog instrument. Comparison and recommendation cards continue to use the existing model-specific `GuitarImage` data.

| Runtime key | Photographer | Actual photograph | Role / difference from the reference |
|---|---|---|---|
| `quizHero` | Wes Hicks | [Electric and acoustic guitars in a music room](https://unsplash.com/photos/several-guitars-beside-of-side-table-MEL-jJnm7RQ) | Real naturally lit room; the reference uses an artificially lit studio. Right-side instruments support a dark text overlay on the left. |
| `compareHero` | Masha | [Electric guitars displayed in a shop window](https://unsplash.com/photos/guitars-displayed-in-a-store-window-YRY0Eo6Yq4s) | Several full, varied electric-guitar shapes in warm light. This is an actual shop window, not a fabricated studio scene containing exactly three guitars. |
| `electricPlayer` | Mila Vasileva | [Close-up of an electric guitarist](https://unsplash.com/photos/a-close-up-of-a-person-playing-an-electric-guitar-gO3BhocajAY) | Generic picking-hand photograph. |
| `acousticPlayer` | Alexander Mass | [Acoustic playing indoors](https://unsplash.com/photos/person-playing-an-acoustic-guitar-indoors-fPiy383YBEM) | Generic acoustic-player photograph. |
| `chordHands` | Alex Kolundzija | [Close-up of a fretting hand](https://unsplash.com/photos/a-hand-plays-guitar-close-up-2KzBcgEMOgM) | Atmosphere, not a certified chord chart or representation of the Practice solver. |

Each publisher photo page displayed “Free to use under the Unsplash License” when read through the web tool on 26 October 2026. The [current Unsplash license page](https://unsplash.com/license) was also read and permits website use, including commercial use and modification, subject to its restrictions. The license is **not represented as Creative Commons**, nor as a blanket permission for trademark/model endorsement. Credits are retained even though the Unsplash license does not require attribution.

The photo pages and license were actually accessible through the web-reading tool. Direct executor requests to the sample photo page and license page returned HTTP401; this limitation is recorded rather than labeling those responses HTTP200. The final successful six-page web-read response has a SHA-256 recorded in `license-evidence.json` and each image record. Only a short license assertion and provenance metadata are retained; an extensive copy of the publisher pages is not redistributed.

Actual CDN JPEG downloads returned HTTP200. Their exact URLs, download times, byte counts, sizes and SHA-256 are in `manifest.json`, with the downloaded source variants retained under `originals/`. These are 1800-pixel variants delivered by the publisher CDN, **not claims that a full-resolution camera master was downloaded**. The original scenes have not been generated, recolored, retouched or composited. The responsive source files preserve the complete 3:2 frame. CSS can crop their editorial framing and apply a dark gradient for readability.

## Runtime assets and checks

- 15 actual local WebP derivatives under `src/assets/discovery/`.
- Hero widths: 480, 960 and 1600 px. Panel widths: 360, 480 and 720 px.
- Total runtime image bytes: **839,000** for all 15 files combined, below one MiB.
- `src/data/discoveryPhotography.js` exposes resolved local URLs and `srcSet`; no temporary or CDN URL is used for browser image loading.
- `python docs/premium-quiz-compare/photos/check-photos.py`: **34/34** actual decoding, checksum, proportion, provenance and file-budget checks passed. Results: `checks.json`.
- `contact-sheet.jpg` shows the five selected photographs for visual review.

`prepare.py` can regenerate WebP derivatives from the retained source variants and historical license manifest. Re-encoding is not a fresh license check; the recorded review date remains 26 October 2026. The initial acquisition used `/tmp/fretline-photo-research`, and the script falls back to the checked-in `originals/` on a fresh workspace.

## Rejected alternatives and source limitations

The existing repository was audited first. Existing brand photographs are real licensed photographs but are primarily close-ups; the existing main home atmosphere is not presented here as newly sourced product photography. Their files and metadata remain unchanged.

ArtHouse Studio’s Pexels rehearsal-room photographs were visually suitable, and the publisher pages showed a free license, but the executor’s CDN requests returned HTTP403. They were **not** added or claimed as acquired. Ben Maffin’s Unsplash electric-guitar collection was also inspected, but its close framing omits headstocks; Masha’s full-instrument shop-window composition was selected instead. No image was invented to disguise these constraints.
