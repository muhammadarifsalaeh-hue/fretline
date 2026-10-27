# Homepage real photography and rights review

Existing repository assets were audited before downloading anything. Model cards retain the existing `GuitarImage` registry; generic instrument photos do not become new model/finish evidence.

## Actual assets used

| Home key | Real source and attribution | License | Use |
|---|---|---|---|
| `quizBackdrop` | [Fender MiM Stratocaster — Yutaka Tsutano](https://commons.wikimedia.org/wiki/File:Fender_MiM_Stratocaster.jpg) | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) | Real electric instrument on dark fabric, used as editorial atmosphere rather than an identified catalog model. |
| `electric` | [Fender strat — Joachim Hensel-Losch; retouched versions by Tkgd2007 and Hohum](https://commons.wikimedia.org/wiki/File:Fender_strat.jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) | Complete electric guitar for the type choice; retains the original blue background. |
| `classical` | [GuitareClassique5 — Martin Möller; derivative by Mouh2jijel](https://commons.wikimedia.org/wiki/File:GuitareClassique5.png) | [CC BY-SA 2.0 Germany](https://creativecommons.org/licenses/by-sa/2.0/de/) | Complete real classical guitar already isolated by the publisher. Publisher transparency is preserved. |
| `bass` | [70's Fender Jazz Bass — Patrick Scales; derivative by Djhé](https://commons.wikimedia.org/wiki/File:70%27s_Fender_Jazz_Bass.png) | Publisher public-domain dedication | Complete real bass already isolated/color-edited by its publisher. No new retouch performed. |
| `acoustic` | [Martin D-28 — IchiroNakagawa](https://commons.wikimedia.org/wiki/File:Martin_D-28.jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Reuses the existing registered owner photo and responsive files to illustrate the acoustic category, without reidentifying it as another model. |
| `heroBackdrop`, `compareBackdrop` | [Music room with acoustic/electric instruments — Wes Hicks](https://unsplash.com/photos/several-guitars-beside-of-side-table-MEL-jJnm7RQ) | [Unsplash License](https://unsplash.com/license) | Reuses existing actual licensed responsive atmosphere photograph. This is a real naturally lit music room, not a newly fabricated studio scene. |

The source and license sections of the four new photographic source pages were actually read on 27 October 2026. Original CDN downloads returned HTTP200. Exact source URLs, source hashes, dimensions and derivative hashes are in [manifest.json](manifest.json), with selected downloaded originals under `originals/`. Discovery-room review remains documented in [the preceding photo acquisition report](../../premium-quiz-compare/photos/README.md); the Martin D-28 photo retains its existing [registry/license file](../../../src/assets/guitars/martin-d-28/LICENSE.md).

Nine local new WebP files total **373,690 bytes**. Sources were proportionally resized without upscaling, cropping, recoloring, new background removal or generated content. Existing source alpha is retained. Files remain under their respective stated license, including share-alike for adapted CC BY-SA works. `check-home-photos.py` decodes every actual image and verifies hashes, dimensions, proportions, transparency, recorded provenance and the 400KiB budget. Rights observations are reviewed facts, not a consequence of those technical tests.

The photo credits section is `/image-credits#home-photography`. It includes source/author/license links and change notes for all new and reused Home sources.

## Exact product photographs and logo limitation

Only Yamaha FG820-12 and Martin D-28 currently have registered **real licensed exact-model photographs**. The existing Pacifica612VIIFM artwork is an illustration and is not relabeled as a real photo. No reviewed electric-model photograph was found that could safely be substituted for the exact catalog model/edition; no product registry or model data was changed. The default real-photo comparison can therefore use FG820-12 and D-28, while the left editorial scene independently contains electric and acoustic instruments.

Nine existing standalone brand-logo assets are retained. A tenth standalone **Córdoba designed mark is still unavailable for permitted reuse**. The current official [Yamaha Guitar Group trademark guidelines](https://yamahaguitargroup.com/trademark-guidelines/) were actually read on 27 October 2026 (page updated 9 September 2025). They distinguish word references from designed logos, requiring a permitted agreement for designed marks and restricting promotional use. The official [Córdoba press page](https://cordobaguitars.com/press/) offers current product press releases but no general standalone-logo permission. No permission is inferred from an image merely being downloadable. The existing honest Córdoba text treatment is retained; no false official logo is drawn and no agreement is claimed.

## Rejected research candidates

`downloads.json` and `additional-downloads.json` retain download observations for candidates inspected during research. Only files named by `manifest.json` are retained under `originals/` and shipped as new assets. Unused candidates included a white-background classical crop, a yellow-wall bass, an Ibanez bass body that cut off the headstock, a diagonal generic acoustic on a sheet, a horizontal transparent Squier photo and an alternate classical cutout. They were not mapped to catalog models or used to pretend exact product photography was acquired.
