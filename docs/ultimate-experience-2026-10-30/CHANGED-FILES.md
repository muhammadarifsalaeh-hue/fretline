# ไฟล์ที่เปลี่ยนแปลง

เทียบกับฐาน `f8084ef` บน `feature/fretline-ultimate-experience`

## Application และตัวตรวจความปลอดภัย

- [index.html](../../index.html)
- [scripts/check-ultimate-experience.mjs](../../scripts/check-ultimate-experience.mjs)
- [src/App.jsx](../../src/App.jsx)
- [src/components/catalog/CatalogCard.jsx](../../src/components/catalog/CatalogCard.jsx)
- [src/components/home/Categories.jsx](../../src/components/home/Categories.jsx)
- [src/components/home/Hero.jsx](../../src/components/home/Hero.jsx)
- [src/components/layout/VisitorExperience.jsx](../../src/components/layout/VisitorExperience.jsx)
- [src/i18n/th.js](../../src/i18n/th.js)
- [src/pages/GuitarDetailPage.jsx](../../src/pages/GuitarDetailPage.jsx)
- [src/pages/PracticePage.jsx](../../src/pages/PracticePage.jsx)
- [src/styles/experience-home.css](../../src/styles/experience-home.css)
- [src/styles/experience-showroom.css](../../src/styles/experience-showroom.css)
- [src/styles/experience-system.css](../../src/styles/experience-system.css)
- [src/styles/experience-tools.css](../../src/styles/experience-tools.css)

## แถบแบรนด์ที่กู้คืน

`src/components/home/Brands.jsx`, `src/hooks/useBrandMarquee.js` และ `src/styles/home-brands.css` ตรงกับ `f8084ef` ทุก byte จึงไม่มี diff จากฐานในสามไฟล์นี้ การนำกรอบออกทำโดยลบ override เฉพาะแบรนด์ 19 rule ใน `experience-home.css` และถอนหัวข้อแบรนด์ออกจาก reveal observer

## รายงานและหลักฐาน

- [README.md](README.md)
- [safety-baseline.json](safety-baseline.json)
- [browser-acceptance.py](browser-acceptance.py)
- [browser-interactions.py](browser-interactions.py)
- [performance-lab.py](performance-lab.py)
- ผลทดสอบใน `tests/` และภาพ browser ใน `screenshots/`

ไม่แก้ `src/data`, รูป/โลโก้ต้นฉบับ, `public`, `src/features`, `src/context`, `src/utils`, SQL, schema, RLS, seed, credentials หรือ config ของ Supabase ไม่เพิ่ม dependencies และไม่เปลี่ยน routes
