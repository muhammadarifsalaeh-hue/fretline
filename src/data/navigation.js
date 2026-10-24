import { t } from '@/i18n';

/** เมนูหลัก (ลำดับตามดีไซน์) */
export const NAV_LINKS = [
  { label: t('nav.home'), href: '/', exact: true },
  { label: t('nav.guitars'), href: '/guitars', mega: true },
  { label: t('nav.brands'), href: '/brands' },
  { label: t('nav.compare'), href: '/compare' },
  { label: t('nav.find'), href: '/find-my-guitar' },
  { label: t('nav.practice'), href: '/practice' },
];

export const BUDGET_LINKS = [
  { label: t('budget.under10'), href: '/guitars?max=10000' },
  { label: t('budget.10to30'), href: '/guitars?min=10000&max=30000' },
  { label: t('budget.30to70'), href: '/guitars?min=30000&max=70000' },
  { label: t('budget.over70'), href: '/guitars?min=70000' },
];

/** ลิงก์ใน Footer: ทุกลิงก์ต้องพาไปหน้าที่มีอยู่จริง */
export const FOOTER_COLUMNS = [
  {
    title: t('footer.shop'),
    links: [
      { label: t('category.electric'), href: '/guitars?type=electric' },
      { label: t('category.acoustic'), href: '/guitars?type=acoustic' },
      { label: t('category.classical'), href: '/guitars?type=classical' },
      { label: t('category.bass'), href: '/guitars?type=bass' },
    ],
  },
  {
    title: t('footer.explore'),
    links: [
      { label: t('nav.brands'), href: '/brands' },
      { label: t('nav.compare'), href: '/compare' },
      { label: t('nav.wishlist'), href: '/wishlist' },
      { label: t('nav.find'), href: '/find-my-guitar' },
    ],
  },
];
