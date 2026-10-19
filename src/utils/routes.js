import { slugify } from './slug';

// URL ของแต่ละหน้า
export const guitarUrl = (slug) => `/guitars/${slug}`;
export const categoryUrl = (id) => `/guitars?type=${id}`;
export const brandUrl = (name) => `/brands/${slugify(name)}`; // หน้าแบรนด์
export const brandCatalogUrl = (name) => `/guitars?brand=${encodeURIComponent(name)}`; // Catalog ที่กรองตามแบรนด์
export const CATALOG_URL = '/guitars';
export const BRANDS_URL = '/brands';
export const WISHLIST_URL = '/wishlist';
