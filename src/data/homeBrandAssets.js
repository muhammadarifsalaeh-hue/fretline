// Shared brand-level editorial assets, never catalog model or finish evidence.
// Provenance, license evidence and hashes: docs/signature-redesign/phase-c/.
const files = import.meta.glob('/src/assets/home-brands/**/*.{svg,png,webp}', {
  eager: true, query: '?url', import: 'default',
});
const file = (kind, id, extension) => files[`/src/assets/home-brands/${kind}/${id}.${extension}`];
const commons = (filename) => `https://commons.wikimedia.org/wiki/File:${filename}`;
const photoCredits = {
  yamaha: ['Yamaha_FGX04_Acoustic_headstock_(2011-11-19_12.06.24_by_Loco_Steve).jpg', 'Loco Steve', 'CC BY 2.0', 'by/2.0'],
  fender: ['1979_Fender_Stratocaster_headstock_(2010-03-18_01.49.11_by_John_Tuggle).jpg', 'John Tuggle', 'CC BY 2.0', 'by/2.0'],
  gibson: ['Gibson_Logo_and_Guitar.jpg', '© Glenn Francis, www.PacificProDigital.com (Toglenn)', 'CC BY-SA 4.0', 'by-sa/4.0'],
  taylor: ['Taylor_Guitar_leaned_on_stool.jpg', 'Lisa Hall-Wilson', 'CC BY 2.0', 'by/2.0'],
  ibanez: ['Ibanez_electric_guitar_ICX120_body.jpg', 'Elmschrat', 'CC BY-SA 4.0', 'by-sa/4.0'],
  prs: ['PRS_Headstock_Close-up.jpg', 'Freebird (Freebird_71)', 'CC BY-SA 2.0', 'by-sa/2.0'],
  epiphone: ['Epiphone_Les_Paul_Special_II_headstock.jpg', 'Elmschrat', 'CC BY-SA 4.0', 'by-sa/4.0'],
  martin: ['Martin_JC-16ME_Aura_soundhole.jpg', 'Elías Gómez', 'CC BY-SA 2.0', 'by-sa/2.0'],
  squier: ['Squier_on_guitar_head.jpg', 'Tharish', 'CC BY-SA 3.0', 'by-sa/3.0'],
  cordoba: ['2020_NAMM_Show_(50783452413).jpg', 'Justin Higuchi', 'CC BY 2.0', 'by/2.0'],
};
const logoFiles = {
  yamaha: 'Yamaha_logo.svg', fender: 'Fender_2020_logo.svg', gibson: 'Gibson_logo.svg',
  taylor: 'Taylor_Guitar_Circular_Logo_Black_and_White.svg', ibanez: 'Ibanez_logo.svg',
  prs: 'PRS_Guitars_logo.svg', epiphone: 'Epiphone_guitars_logo.svg',
  martin: 'Martin_Guitars_logo_2023.svg', squier: 'Squier_guitars_logo.png',
};
export const HOME_BRAND_ORDER = ['yamaha', 'fender', 'gibson', 'taylor', 'ibanez', 'prs', 'epiphone', 'martin', 'squier', 'cordoba'];
export const HOME_BRAND_ASSETS = Object.fromEntries(HOME_BRAND_ORDER.map((id) => {
  const credit = photoCredits[id];
  // Use an honest typographic name until a suitable standalone Córdoba mark is
  // available. Preserve the licensed photograph and its wordmark provenance.
  const typographic = id === 'cordoba';
  return [id, {
    logo: typographic ? null : file('logos', id, id === 'squier' ? 'png' : 'svg'),
    logoKind: typographic ? 'typographic' : 'mark',
    photo: file('photos', id, 'webp'),
    logoSource: logoFiles[id] ? commons(logoFiles[id]) : null,
    photographedWordmarkSource: typographic ? commons(credit[0]) : null,
    photoSource: credit ? commons(credit[0]) : null,
    author: credit?.[1], license: credit?.[2],
    licenseUrl: credit ? `https://creativecommons.org/licenses/${credit[3]}/` : null,
  }];
}));
