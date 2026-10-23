# Phase C brand mark research

> Historical Phase C report for commit14f92ca. Córdoba now has licensed guitar imagery and a genuine photographed wordmark; see [Córdoba follow-up](../../cordoba-update/README.md). Initial counts and fallback descriptions below record the earlier version.


Access date: **2026-10-23**. Scope: the ten brands already present in Fretline. No guitar data, IDs, model counts, or application state are changed by this research.

Nine real brand marks have an explicit copyright reuse basis on Wikimedia Commons. Each selected file-description page was opened and its identity, author/source, licensing section, and original-file link checked. These are existing manufacturer marks, not lettering generated for Fretline. The copyright classification is the Commons file-page statement; it does not imply that the manufacturer endorses or licensed Fretline. Trademark rights remain with their respective owners.

The downloadable originals and provenance are recorded in [brand-logos.json](brand-logos.json). Download success and appearance in the application must be checked separately by the implementing agent.

| Brand | Selected file | Copyright basis recorded on Commons | Source listed by file page |
| --- | --- | --- | --- |
| Yamaha | [Yamaha logo.svg](https://commons.wikimedia.org/wiki/File:Yamaha_logo.svg) | PD-Japan-expired, PD-textlogo, Public Domain Mark | Yamaha; own work using yamaha.co.jp |
| Fender | [Fender 2020 logo.svg](https://commons.wikimedia.org/wiki/File:Fender_2020_logo.svg) | PD-shape | SVG from Fender's official shop |
| Gibson | [Gibson logo.svg](https://commons.wikimedia.org/wiki/File:Gibson_logo.svg) | PD-textlogo | Extracted from a Gibson guitar PDF; converted by Tkgd2007 |
| Taylor | [Taylor Guitar Circular Logo Black and White.svg](https://commons.wikimedia.org/wiki/File:Taylor_Guitar_Circular_Logo_Black_and_White.svg) | PD-textlogo | Taylor Guitars official circular SVG |
| Ibanez | [Ibanez logo.svg](https://commons.wikimedia.org/wiki/File:Ibanez_logo.svg) | PD-textlogo | Ibanez; source image at musicmaker.ie |
| PRS | [PRS Guitars logo.svg](https://commons.wikimedia.org/wiki/File:PRS_Guitars_logo.svg) | PD-textlogo | PRS official support attachment |
| Epiphone | [Epiphone guitars logo.svg](https://commons.wikimedia.org/wiki/File:Epiphone_guitars_logo.svg) | PD-textlogo | Epiphone/Gibson; based on a retailer image |
| Martin | [Martin Guitars logo 2023.svg](https://commons.wikimedia.org/wiki/File:Martin_Guitars_logo_2023.svg) | PD-textlogo | C.F. Martin & Co.; martinguitar.com |
| Squier | [Squier guitars logo.png](https://commons.wikimedia.org/wiki/File:Squier_guitars_logo.png) | PD-textlogo | Fender official newsroom logos page |
| Córdoba | No qualified asset selected | Not established | Use the existing plain-text fallback |

## Selection notes

- **Yamaha:** use Yamaha Corporation's musical-instrument mark, including its tuning-fork symbol, rather than Yamaha Motor's different mark. The selected `Yamaha logo.svg` explicitly records both Japanese expired copyright and the US text-logo classification. Commons notes that the SVG has validation errors; verify browser rendering after download. `Yamaha logo dark.svg` is a smaller alternative, but its page has a missing US copyright-tag warning, so it was not selected.
- **Taylor:** the monochrome circular mark is directly sourced to Taylor's official SVG and resembles the approved reference more closely than plain lettering. Another circular file has inconsistent upload-source history; it was not selected.
- **Gibson:** the selected file has a 300 × 190 view box, so allow for internal whitespace when fitting it inside a card. Preserve the mark's proportions; do not redraw it.
- **Squier:** the transparent PNG is sourced to Fender's newsroom and records PD-textlogo. The similarly named SVG additionally records CC BY-SA 4.0; the selected PNG avoids silently ignoring that extra attribution/share-alike declaration. A derived/optimized PNG or WebP should retain this provenance.
- **Córdoba:** targeted searches for the manufacturer mark on Commons, public-domain/Creative-Commons sources, and the manufacturer's press/logo material did not establish a usable asset. Search results for cities, sports teams, broadcasters, and shopping centres are unrelated and were rejected. This is a limitation of this search, not a claim that no usable mark exists anywhere. The user explicitly permits temporary text when a qualified logo is unavailable.
- Monochrome presentation through CSS does not create a new manufacturer logo. Preserve original files/provenance, and record any actual file conversion or edits in the application asset registry.

## Photographs

This logo search grants no new rights to manufacturer product photographs. Do not use one brand's product image as another brand's card background. Existing Fretline licensed Yamaha and Martin photographs remain the only already-established brand-specific photography identified at the start of this task. Any additional cinematic background needs its own identity and license record; a general reference image or an accessible product URL does not establish photo reuse rights.

A follow-on search identified seven optional owner/photographer images with explicit Commons license evidence in [brand-photographs.json](brand-photographs.json). These are candidate **brand editorial backgrounds**, not model-specific Catalog photographs. Their sources were opened and licensing checked, but the research agent did not download or visually approve them. The implementing agent must inspect them and carry attribution, modification notices, and the applicable share-alike license on any adapted image. A qualified Córdoba guitar photograph was not selected.

## Recheck procedure

1. Open the linked Commons file page and confirm its licensing and source are still as recorded.
2. Download the linked original; confirm it is an image, not an HTML error page.
3. Inspect the mark visually and verify SVG safety, aspect ratio, and rendering.
4. Register the local file and provenance in Fretline's existing image/brand system.
5. Preserve an appropriate source/credit record and trademark attribution; do not imply endorsement.
