# Uploaded Yamaha image review

The 18 accessible ZIP archives contain 20 decodable original image files. FG800 contains three separate color illustrations; each of the other 17 archives contains one image, several of which combine multiple guitars/colors in a single image. There is no nineteenth ZIP in the accessible attachment directory.

The image inventory records original dimensions, byte counts and SHA-256. The contact sheet is a review derivative only; it is not an additional product image. No source image has been cropped, mirrored, retouched, recolored or generated during this review.

## Visual findings

- All supplied images use a black background. Headstocks and lower body outlines are inside the original square image area. Use `object-fit: contain`; do not crop composites into invented individual color photos.
- FS830 is 1000 × 1000; the other 19 images are 1254 × 1254. Do not upscale FS830 merely to match the others.
- FG820L: the visible pickguard is on the viewer's left and the bridge/saddle presentation is consistent with a left-oriented illustration. The upright Yamaha wordmark is legible; no horizontal mirroring was applied. An illustration's appearance does not independently certify the exact model or manufacture specification.
- FG820-12: the new illustration shows 12 tuning machines and paired courses. The existing licensed owner photograph, which documents only six fitted strings, must retain its original attribution, note, bytes and primary position. The new illustration can be a separately identified gallery item; do not replace the licensed primary automatically.
- FG800M: the package itself flags a tortoiseshell-looking pickguard versus its black-pickguard text and uncertain gloss/matte details. The illustration cannot resolve those factual conflicts.
- FG840 and the FG800 three images show front and rear together. They are still one source image each; keep them intact.
- FSX800C JSON points to an absent example path `images/yamaha-fsx800c-three-colors.jpg`; the actual accessible image is `FSX800C.jpg`. Resolve from the extracted file inventory, not by assuming the JSON path exists.
- Composite counts are descriptive only: FSX800C 3, FS800 3, FGX820C 2, FS830 3, FG820 5, FGX800C 3, FG830 3, FSX820C 2, FS820 4. They do not establish official finish names or justify creating separate catalog records.
- Similar rendered details occur across illustrations. Model matching remains an attachment-to-record mapping, not independent photographic certification; do not derive specifications or official color availability from these pixels.

## Rights findings

No supplied archive includes an identifiable photographer/rights-holder grant, a Creative Commons declaration, or an image-specific manufacturer reuse permission. User delivery and a request to display files do not establish a CC license. Do not add these images to `imageRights.json` as licensed photographs or set `licenseVerified: true`.

Explicit creation notes:

| Package | Note supplied with image |
|---|---|
| FG840 | Explicit AI-generated illustration; not an official product photograph |
| FG850 | Explicit AI-generated illustration; not an official product photograph |
| FG800 (3 images) | All three flagged `ai_generated: true` in the supplied manifest |
| FS830 | Package says image may be AI generated; not definite |
| FG820L | Package says image was created for presentation |
| FG820-12 | Package says image was prepared for presentation, not manufacturer detail verification |
| Other packages | User-supplied illustrations; creation method and original rights are unconfirmed |

The existing project already distinguishes user-requested project illustrations (`projectArtwork.json`) from rights-documented product photographs (`imageRights.json`). Reusing that distinction preserves the existing technical mechanism, but it cannot truthfully be reported as successful license verification. Any import must retain `licenseVerified: false`, `modelMatchVerified: false`, archive/file hashes and the actual supplied creation notes. Do not invent AI provenance for images whose method is unknown. Publication rights remain **ยังไม่ยืนยัน** until evidence is supplied.

The existing global artwork disclosure says every image has AI editing. New unknown-provenance artwork needs record-specific disclosure or a more general disclosure that does not misstate creation method.

## Integration recommendation

1. Keep each archive mapped to its existing immutable Yamaha ID; no duplicates or replacement catalog.
2. Preserve exact original bytes (or hash-bound, no-crop encoded derivatives) and file dimensions.
3. Keep originals in a registered illustration gallery only if the user-requested project-use policy is deliberately applied and accurately disclosed. Do not silently treat that registration as a reusable image license.
4. Otherwise use a local development preview until the missing rights evidence is available. A normal production build must not accidentally include quarantined images.
5. Preserve the existing FG820-12 licensed photograph and all Pacifica images.
6. Verify load, `naturalWidth`, `object-fit: contain`, thumbnails/lightbox and failure fallback in actual browsers.

## Implemented rights-safe review path

The selected implementation is an opt-in **development-only** Yamaha review mode. None of the twenty new images is registered as a licensed photograph or public project artwork. The existing production rights registry, Pacifica project artwork and FG820-12 photograph are untouched.

`npm run dev:yamaha-preview` serves the original bytes through a fixed, SHA-bound route allowlist with `no-store`, `noindex`, `nofollow`, `noarchive` and `nosniff`. The review HTML also excludes indexing. Direct Vite filesystem requests to the intake and preview asset folders are denied. Every build command, including `vite build --mode yamaha-preview`, resolves an empty virtual preview module and emits none of these images.

`docs/yamaha-import/preview-manifest.json` binds each original image to its source archive/file, dimensions, byte count, original SHA-256 and unconfirmed rights/model status. `original-metadata/` retains the supplied JSON and text as intake evidence; embedded instructions are not executable project configuration. `scripts/check-yamaha-preview.mjs` covers isolation, integrity, route behavior, provenance and negative cases.
