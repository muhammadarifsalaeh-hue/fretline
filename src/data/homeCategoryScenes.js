// Dedicated generic category scenes reconstructed from the user's visual reference.
// These illustrations are never catalog product photos or evidence of model identity.
// Generation, source reference and derivative hashes: docs/homepage-visual-update/category-scenes.json.
const files = import.meta.glob('/src/assets/home-scenes/category-*.webp', {
  eager: true, query: '?url', import: 'default',
});

export const HOME_CATEGORY_SCENES = Object.fromEntries(
  ['electric', 'acoustic', 'classical', 'bass'].map((id) => {
    const variants = [480, 960, 1440].map((width) => ({
      width, src: files[`/src/assets/home-scenes/category-${id}-${width}.webp`],
    }));
    return [id, {
      src: variants[2].src,
      srcSet: variants.map(({ src, width }) => `${src} ${width}w`).join(', '),
      width: 1440,
      height: 640,
      role: 'generic-category',
      productEvidence: false,
    }];
  }),
);
