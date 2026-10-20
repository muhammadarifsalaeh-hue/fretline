# Fretline Phase 8 — Premium UI/UX Polish & Quality Assurance

พัฒนาต่อจาก repository เดิมบน `master` / baseline `79025fe4c80f1bbb43a072bbfa6f79871da2fdbd` ไม่มีการสร้างโปรเจกต์ใหม่หรือเพิ่ม dependency ของแอป

## ขอบเขตข้อมูล

คง Catalog 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น รวมถึง ID, แหล่งข้อมูลและไฟล์ภาพเดิมทั้งหมด ไม่มีการเพิ่มราคา สเปก รีวิว หรือเลื่อนสถานะเป็น verified

| แบรนด์ | จำนวนรุ่น |
|---|---:|
| Córdoba | 20 |
| Epiphone | 20 |
| Fender | 20 |
| Gibson | 20 |
| Ibanez | 20 |
| Martin | 20 |
| PRS | 20 |
| Squier | 20 |
| Taylor | 20 |
| Yamaha | 20 |
| **รวม** | **200** |

ข้อมูลทั้ง 200 รุ่นยังเป็น `partial` รูปถ่ายที่มีบันทึกสิทธิ์ยังมี 1 รุ่น และ 199 รุ่นใช้ภาพประกอบ SVG เดิมที่วาดในโปรเจกต์ ภาพประกอบใหม่เป็นเพียงการปรับรูปแบบการแสดงผล ไม่ใช่ภาพถ่ายรุ่นจริง

`yamaha-c40` และ `gretsch-g2420-streamliner` ยังคงอยู่ในไฟล์สำรองเดิม เปิด Detail จากลิงก์เก่าและใช้ใน Wishlist/Compare ที่บันทึกไว้ได้ โดยไม่นับในยอด Catalog

## Reference และการปรับปรุง

เปิดดูภาพ Reference เดิม `4-รูปภาพ-4.jpg` ที่แนบในบทสนทนาได้ ใช้เทียบโทนดำ–ทอง สัดส่วนการ์ด กรอบ เส้นแบ่ง การจัดลำดับเนื้อหาและรูปแบบหน้า เปรียบเทียบด้วยสายตาจากภาพหน้าจอจริง ไม่อ้างความเหมือนแบบ pixel-perfect เพราะ Reference เป็นภาพรวมหลายหน้า และไม่มีภาพถ่ายที่ได้รับสิทธิ์ครบทุกโมเดล

- **Homepage:** คง Hero และลำดับ section เดิม เพิ่มสถานะข้อมูลบนการ์ด ปรับคีย์บอร์ดของแท็บและ carousel, โครงสร้างสถิติแบบ semantic, หยุดแถบแบรนด์เมื่อ focus และป้องกันเพิ่ม Compare เกิน 4 รุ่น
- **Catalog:** ค้นหาแบบไม่ต้องพิมพ์ accent เช่น Córdoba/cordoba และเครื่องหมายรุ่น D-18/D18, cache ข้อความค้นหา, แสดง 10 แบรนด์ตั้งแต่ต้น, จัดประวัติ URL ให้ย้อน filter/sort/search/page ได้, ทำความสะอาด query ซ้ำหรือไม่ถูกต้อง, แสดงช่วงและจำนวนผลลัพธ์จริง, ปรับ drawer และจุดแตะ/โฟกัส
- **Guitar Detail:** ใช้พื้นที่ Gallery เต็มเมื่อมีเพียง Placeholder, ไม่สร้าง thumbnail ปลอม, คงภาพจริงพร้อมเครดิต, เพิ่มสถานะ Compare เต็ม และการเลือกสีด้วยปุ่มลูกศร
- **Compare:** โฟกัสช่องค้นหาตอนเปิด picker, แสดงจำนวนผลการค้นหาจากข้อมูลจริง, deferred search, คืน focus หลังลบ และปรับโครงสร้างสำหรับโปรแกรมอ่านหน้าจอ
- **Quiz:** คงคำถาม/สูตร/น้ำหนักเดิมทั้งหมด ผูกคำอธิบายกับคำตอบและ radiogroup และย้าย focus ไปหัวข้อผลลัพธ์เมื่อจบ
- **Brands / Brand Detail:** คงจำนวนรุ่นจากฐานข้อมูลเดิม ปรับกรอบและตัวอักษรให้สอดคล้อง และคืน focus หลังล้างคำค้น
- **Wishlist:** คง localStorage และการจัดการรุ่นที่พักไว้ ใช้ Placeholder/กรอบ/สถานะ/จุดแตะที่สอดคล้องกับทุกหน้า
- **ส่วนร่วม:** เพิ่ม skip link, focus states, เมนูมือถือที่ใช้ hook จัดการ dialog ร่วม, ปิดเมนูเมื่อหมุนจอเข้าสู่ desktop, active state ของเมนูล่าง, safe-area สำหรับ iPad/iPhone, ป้องกัน input zoom บนจอสัมผัส, ปรับ footer contrast และรูปตกแต่ง
- **ภาพ:** Placeholder ระบุแบรนด์/รุ่นในพื้นที่ที่เพียงพอ พร้อมข้อความว่าเป็นภาพประกอบ ตัวการ์ดแสดงชื่อเต็มเสมอ ใช้ขนาดกรอบคงที่และ lazy loading สำหรับภาพรายรุ่น ภาพสำคัญใช้ eager/high priority โดยรองรับ React 18

## ผลทดสอบ

ผลสุดท้ายทดสอบกับ Vite production preview ในเครื่อง (`http://127.0.0.1:4188`) โดยไม่เพิ่ม dependency ให้แอป

| การตรวจ | ผล |
|---|---|
| `npm run build` | ผ่าน ดู `qa-phase8-review/build-final.txt` |
| `npm run catalog:check` | ผ่าน — 200 active / 10 แบรนด์ / แบรนด์ละ 20 / ไม่มีซ้ำ |
| `npm run images:check` | ผ่านสิทธิ์และ integrity — ภาพจริง 1, Placeholder 199 ไม่ใช่ภาพครบ 200 |
| ชุด Logic Phase 4–7 | ผ่าน 71/71 ข้อ |
| `npm run phase8:check` | ผ่าน 18/18 ข้อ รวม hash แหล่งข้อมูลเดิมและการค้นหา |
| Core browser flows | ผ่าน 54/54 ข้อ: Catalog, Detail, Wishlist, Compare 2–4, Quiz, archive URLs |
| ปุ่มกรอง/ค้นหา/Sorting และ Back/Forward จริง | ผ่าน 11/11 ข้อ |
| Keyboard / dialog / ปิด–เปิด animation | ผ่าน 12/12 ข้อ รวม Tab, Shift+Tab, Escape และเปลี่ยนขนาดจอ |
| ฉีดข้อผิดพลาดและสถานะพิเศษ | ผ่าน 6/6 ข้อ: loading, failed chunk, retry, empty query, failed photo, unknown brand |
| เปิด Detail จริงใน browser | ครบ 200/200 รุ่น ชื่อตรงข้อมูล ไม่มี runtime/console/request errors |
| Brand Detail และลิงก์รุ่น | ครบ 10/10 แบรนด์ ลิงก์ Detail รวม 200 รุ่นตรง ID ใน Catalog |
| Responsive | ผ่าน 50/50 กรณี: 10 หน้าที่ 1440, 1024, 768, 390, 320px ไม่มี document overflow หรือรูปเสีย |
| Compare บนจอแคบ | ตรวจ 4 รุ่นจริงทุกขนาด เลื่อนอยู่ในตาราง ไม่ดันหน้าล้น |
| axe-core 4.10.3 | ตรวจ 29 หน้า/สถานะ dialog ไม่พบ violation ตาม WCAG A/AA tags ที่ตรวจ มีรายการที่ต้องตรวจด้วยคนแยกใน JSON |
| Screenshots | 53 ภาพ responsive + 4 ภาพสถานะผิดพลาด/โหลด + ภาพรวม 1 ภาพ |
| `git diff --check` | ผ่าน |

Console/Runtime/failed-request errors เป็นศูนย์ใน normal-flow audits ส่วน `states-results.json` บันทึกข้อผิดพลาดที่จงใจฉีดแยกไว้ ไม่รวมเป็นการใช้งานปกติ

การตรวจเริ่มต้นพบและแก้ปัญหา contrast ของ footer, โครงสร้างสถิติ `dl` และตัวห่อแถว Compare ของ ARIA ดู `qa-phase8-accessibility/initial-findings.json` เทียบกับ `accessibility-results.json` หลังแก้ อีกปัญหาที่ browser พบคือ focus เข้าหน้าต่างที่ยังติด CSS visibility transition ไม่ได้ จึงปรับ hook ให้รอจนเป้าหมายมองเห็น และตรวจซ้ำทั้ง animation ปกติและ reduced motion

หลักฐานสรุป: [`qa-phase8-review/summary.json`](qa-phase8-review/summary.json), [`qa-phase8/browser-phase8-results.json`](qa-phase8/browser-phase8-results.json), [`ผล axe`](qa-phase8-accessibility/accessibility-results.json) และ [`ผล Responsive`](qa-phase8-review/responsive-results.json)

### ภาพหน้าจอ

- [Catalog Desktop 1440](qa-phase8-review/catalog-1440.png) / [Tablet 1024](qa-phase8-review/catalog-1024.png) / [Tablet 768](qa-phase8-review/catalog-768.png) / [Mobile 390](qa-phase8-review/catalog-390.png) / [Mobile 320](qa-phase8-review/catalog-320.png)
- [Homepage](qa-phase8-review/home-1440.png), [Detail](qa-phase8-review/detail-1440.png), [ภาพจริง](qa-phase8-review/photo-detail-1440.png)
- [Compare 4 รุ่น Desktop](qa-phase8-review/compare-1440.png) / [Mobile](qa-phase8-review/compare-390-full.png)
- [Quiz](qa-phase8-review/quiz-390.png), [Results](qa-phase8-review/quiz-results-1440.png), [Brands](qa-phase8-review/brands-1440.png), [Brand Detail](qa-phase8-review/brand-detail-768.png), [Wishlist](qa-phase8-review/wishlist-390.png)

### Performance

คงการแบ่ง route chunks และ catalog/vendor chunk เดิม JavaScript chunk ใหญ่สุด 429,598 bytes จากไฟล์จริง ไม่มี chunk เกิน 500 KB ค่าที่แสดงโดย Vite บางบรรทัดเป็นความยาวสตริงซึ่งต่างจากจำนวน UTF-8 bytes ของข้อความไทย จึงเก็บขนาดไฟล์จริงและ gzip estimates ไว้ใน [`final-asset-sizes.json`](qa-phase8-review/final-asset-sizes.json) Dependency และ lockfile ไม่เปลี่ยน

ดูวิธีรันทดสอบซ้ำใน [`qa-phase8-review/README.md`](qa-phase8-review/README.md)

## ข้อจำกัดที่ยังเหลือ

- ตรวจบน Chromium ใน Linux ด้วย Playwright ไม่มี iPad หรือ Safari จริง จึงยังต้องตรวจ Safari บนอุปกรณ์จริงเพิ่ม
- ยังไม่มีราคาเงินบาทหรือรีวิวที่มีหลักฐาน ไม่สามารถพิสูจน์การเรียงราคา/ช่วงราคาในข้อมูลจริงที่มีตัวเลขได้ ทดสอบพฤติกรรมราคาที่ไม่ทราบและกรณีทดสอบ logic เดิมแทน
- ยังมี 199 Placeholder ไม่มีการใช้ภาพกีตาร์รุ่นอื่นแทน
- axe-core เป็นการตรวจอัตโนมัติเฉพาะกฎที่รองรับ ไม่รับรอง WCAG ทั้งหมด และไม่แทนการใช้ screen reader จริง
- การวัดขนาด bundle/asset เป็นการตรวจในเครื่อง ไม่ใช่ผล Lighthouse หรือความเร็วผ่านเครือข่ายผู้ใช้จริง

## อัปเดต Codespaces / Safari บน iPad

เปิด Codespace ของ repository นี้ แล้วรัน:

```bash
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

เปิด `Ports` → `5173` → `Open in Browser` หาก server เดิมยังทำงาน ให้หยุดด้วย `Ctrl+C` แล้วรัน dev อีกครั้ง ใช้ Preview แบบ Private และล็อกอินบัญชีที่มีสิทธิ์ repository ไม่ต้องส่งรหัสผ่านหรือ token ในแชท

Phase 8 สิ้นสุดเมื่อ commit และ push งานที่ผ่านการตรวจแล้ว ไม่เริ่ม Phase 9 อัตโนมัติ

## Files Modified / Added

ไฟล์แอปและสคริปต์ที่เปลี่ยน รวมถึงรายงานและหลักฐานเพิ่มเติมใน `docs/qa-phase8*`:

```text
.gitignore
README.md
index.html
package.json
scripts/check-phase8-catalog.mjs
scripts/check-phase8.mjs
src/App.jsx
src/components/brands/BrandsToolbar.jsx
src/components/catalog/ActiveFilters.jsx
src/components/catalog/CatalogCard.jsx
src/components/catalog/CatalogToolbar.jsx
src/components/catalog/FilterCheckbox.jsx
src/components/catalog/FilterGroup.jsx
src/components/catalog/FilterPanel.jsx
src/components/catalog/MobileFilterDrawer.jsx
src/components/compare/CompareTable.jsx
src/components/compare/GuitarPicker.jsx
src/components/detail/ColorSwatches.jsx
src/components/detail/GuitarGallery.jsx
src/components/detail/StickyGuitarBar.jsx
src/components/guitar/GuitarCard.jsx
src/components/guitar/ImagePlaceholder.jsx
src/components/home/Brands.jsx
src/components/home/FeaturedGuitars.jsx
src/components/home/HeroStats.jsx
src/components/layout/BottomBar.jsx
src/components/layout/CompareBar.jsx
src/components/layout/Footer.jsx
src/components/layout/MegaMenu.jsx
src/components/layout/MobileMenu.jsx
src/components/layout/Navbar.jsx
src/components/quiz/QuizFlow.jsx
src/components/quiz/QuizOption.jsx
src/components/quiz/QuizResults.jsx
src/components/search/SearchBar.jsx
src/components/ui/Button.jsx
src/components/ui/DiscoveryHeading.jsx
src/components/ui/SectionHeading.jsx
src/components/ui/SmartImage.jsx
src/components/ui/Tabs.jsx
src/hooks/useCatalogFilters.js
src/hooks/useDialogFocus.js
src/i18n/en.js
src/i18n/th.js
src/main.jsx
src/pages/CatalogPage.jsx
src/pages/ComparePage.jsx
src/pages/GuitarDetailPage.jsx
src/styles/polish.css
src/utils/search.js
```
