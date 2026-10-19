/** 'Córdoba' → 'cordoba', 'PRS' → 'prs' (ใช้เป็น id/URL ของแบรนด์) */
export const slugify = (text) =>
  text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
