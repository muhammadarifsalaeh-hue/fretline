# ไฟล์ที่เปลี่ยนในงาน Signature Experience

ทุกไฟล์ด้านล่างอยู่บน Feature branch งานนี้ ไม่มีไฟล์ข้อมูลสินค้า Admin/Auth, Supabase หรือ SQL ถูกแก้ไข

## Source และสคริปต์

- [scripts/check-phase5.mjs](../../scripts/check-phase5.mjs)
- [scripts/check-signature-safety.mjs](../../scripts/check-signature-safety.mjs)
- [src/App.jsx](../../src/App.jsx)
- [src/components/compare/CompareSection.jsx](../../src/components/compare/CompareSection.jsx)
- [src/components/detail/ImageAttribution.jsx](../../src/components/detail/ImageAttribution.jsx)
- [src/components/home/Brands.jsx](../../src/components/home/Brands.jsx)
- [src/components/home/Categories.jsx](../../src/components/home/Categories.jsx)
- [src/components/home/FindMyGuitar.jsx](../../src/components/home/FindMyGuitar.jsx)
- [src/components/home/GuitarPracticeCard.jsx](../../src/components/home/GuitarPracticeCard.jsx)
- [src/components/home/Hero.jsx](../../src/components/home/Hero.jsx)
- [src/components/layout/PublicExperience.jsx](../../src/components/layout/PublicExperience.jsx)
- [src/components/quiz/QuizHero.jsx](../../src/components/quiz/QuizHero.jsx)
- [src/components/quiz/QuizResults.jsx](../../src/components/quiz/QuizResults.jsx)
- [src/components/ui/DiscoveryHeading.jsx](../../src/components/ui/DiscoveryHeading.jsx)
- [src/i18n/en.js](../../src/i18n/en.js)
- [src/i18n/th.js](../../src/i18n/th.js)
- [src/pages/BrandDetailPage.jsx](../../src/pages/BrandDetailPage.jsx)
- [src/pages/BrandsPage.jsx](../../src/pages/BrandsPage.jsx)
- [src/pages/CatalogPage.jsx](../../src/pages/CatalogPage.jsx)
- [src/pages/ComparePage.jsx](../../src/pages/ComparePage.jsx)
- [src/pages/ImageCreditsPage.jsx](../../src/pages/ImageCreditsPage.jsx)
- [src/pages/NotFoundPage.jsx](../../src/pages/NotFoundPage.jsx)
- [src/pages/WishlistPage.jsx](../../src/pages/WishlistPage.jsx)
- [src/styles/signature/catalog.css](../../src/styles/signature/catalog.css)
- [src/styles/signature/foundation.css](../../src/styles/signature/foundation.css)
- [src/styles/signature/home.css](../../src/styles/signature/home.css)
- [src/styles/signature/index.css](../../src/styles/signature/index.css)
- [src/styles/signature/studio.css](../../src/styles/signature/studio.css)
- [src/styles/signature/tools.css](../../src/styles/signature/tools.css)

## Audit และหลักฐาน

- [README.md](README.md)
- [AUDIT.md](AUDIT.md)
- [safety-baseline.json](safety-baseline.json)
- [IMAGE-GAPS.md](IMAGE-GAPS.md)
- [browser-routes.py](browser-routes.py)
- [browser-interactions.py](browser-interactions.py)
- [browser-accessibility.py](browser-accessibility.py)
- ผลทดสอบและภาพใน `tests/` และ `screenshots/`

ไม่กู้คืนหรือเขียนทับไฟล์จาก Git ในรอบนี้ ใช้ฐานล่าสุดที่มีอยู่ สร้าง Tag และ Archive ไว้ก่อนเริ่มสำหรับย้อนกลับ
