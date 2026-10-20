const LICENSES = {
  'CC0-1.0': 'https://creativecommons.org/publicdomain/zero/1.0',
  'CC-BY-2.0': 'https://creativecommons.org/licenses/by/2.0',
  'CC-BY-4.0': 'https://creativecommons.org/licenses/by/4.0',
  'CC-BY-SA-2.0': 'https://creativecommons.org/licenses/by-sa/2.0',
  'CC-BY-SA-3.0': 'https://creativecommons.org/licenses/by-sa/3.0',
  'CC-BY-SA-4.0': 'https://creativecommons.org/licenses/by-sa/4.0',
};
const https = (value) => { try { return new URL(value).protocol === 'https:'; } catch { return false; } };
const realDate = (value) => /^\d{4}-\d{2}-\d{2}$/.test(value ?? '') && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;

/** A local photo is publishable only after a human records its model and rights. */
export function hasImageRights(image, guitarId) {
  return Boolean(image && image.guitarId === guitarId && image.author?.trim()
    && Object.prototype.hasOwnProperty.call(LICENSES, image.license)
    && image.licenseUrl?.replace(/\/$/, '') === LICENSES[image.license]
    && https(image.sourceUrl) && realDate(image.checkedOn)
    && image.modelMatchNote?.trim() && image.changes?.trim());
}
