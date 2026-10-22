# Fretline — Phase B: Premium Design System & Shared Components

Phase B พร้อมตรวจบนโปรเจกต์เดิม `master` ต่อจาก `e01c137` (application baseline `82fbe9b`) ตาม Styleboard ที่ผู้ใช้อนุมัติ **หยุดที่จุดตรวจนี้ก่อนเริ่ม Phase C: Homepage Redesign**

## เปิดดู Before / After

ภาพทั้งหมดมาจากเว็บไซต์จริงใน Chromium ไม่ใช่ Styleboard หรือภาพจำลองหน้าเว็บ

| หน้าจอ | ภาพเทียบ Catalog | ภาพ After ตัวอย่าง |
|---|---|---|
| Desktop 1440 × 1000 | [Before / After](review-desktop.png) | [Homepage](after/home-desktop.png) · [Detail](after/detail-desktop.png) · [Compare](after/compare-desktop.png) |
| Tablet 768 × 1024 | [Before / After](review-tablet.png) | [Homepage](after/home-tablet.png) · [Detail](after/detail-tablet.png) · [Compare](after/compare-tablet.png) |
| Mobile 390 × 844 | [Before / After](review-mobile.png) | [Homepage](after/home-mobile.png) · [Detail](after/detail-mobile.png) · [Compare](after/compare-mobile.png) |

[เปิดรายงานภาพเปรียบเทียบครบ36คู่](review.html) — ครอบคลุม Homepage, Catalog, Detail, Brands, Brand Detail, Compare, Quiz welcome/question/results และ Wishlist รวม full-page และ empty states; [manifest](review-manifest.json) ไม่มีภาพขาด

ใน Vite dev เดิม เปิด path `/docs/signature-redesign/phase-b/review.html` ต่อท้าย Forwarded Address ของ Codespaces เพื่อดู HTML นี้พร้อมภาพทั้งหมด

## สิ่งที่เปลี่ยน

- **Design tokens:** palette ดำ/charcoal, warm white, secondary `#B3B3AA`, muted `#96968E`, champagne focus; typography roles, spacing, radius, shadows, control sizes, header/tray layers และ motion duration ใช้ร่วมผ่าน [`src/styles/tokens.css`](../../../src/styles/tokens.css) และ Tailwind aliases เดิม รองรับ opacity utilities โดยไม่เพิ่ม dependency หรือ font service
- **Typography:** local Anuphan / Instrument Serif เดิม, body line-height1.8, หัวข้อไทย1.4 พร้อม natural tracking, เลิก blanket `!important`; supporting roles ใน CSS ใช้ caption13pxและขนาดหัวข้อร่วม ปรับจุดตัดคำหมวดกีตาร์ภาษาไทยโดยไม่ตัด “คลาสสิก” กลางคำ
- **Navbar / mobile navigation:** ไอคอน20pxและพื้นที่กด44px, เมนูกีตาร์มี disclosure แยกจากลิงก์ Catalog สำหรับ keyboard/touch, Enter/ArrowDown/Escape, outside click, คืน focus และซ่อนเมนูปิดด้วย `inert`; ข้อมูลจำนวน Compare/Wishlist ยังมาจาก ShopContext
- **Buttons / cards:** control radius8px, card radius12px, border/surface feedback ที่เรียบขึ้น, ขนาดภาพ4:5และ`object-contain`; เอา hover scaling ของรูปใน Catalog/Home/Compare/MegaMenuออก ไม่มีการเปลี่ยนไฟล์ภาพ การ์ดและตัวเลือกสีใช้ handlers เดิม
- **Footer / loading:** lazy-route fallback จองความสูงอย่างน้อยหนึ่ง viewport ทำให้ Footer ไม่โผล่มาในช่วงโหลดแล้วกระโดดลง; footer links/heading/notes ใช้บทบาทตัวอักษรร่วม และ watermark มีอัตราส่วนพื้นที่ชัดเจน
- **Price Filter:** แยกราคาสูงสุดที่ทราบจากขอบเขตงบประมาณ; ไม่จำกัด URL ไว้ที่34,000บาท เมื่อไม่มี maximum ให้หมายถึงไม่จำกัด และเก็บ finite thresholds ตามคำขอจริง ราคาไม่ทราบไม่ผ่าน explicit budget; reset คืน200รุ่น; slider ใช้ DOM bounds แบบ finite, endpoint แบบไม่จำกัด, aria-valuetext และ thumb hit box44px
- **Compare:** ค่าที่เหมือนกันและคำอธิบายอ่านได้ด้วยสีทึบ มีขนาดข้อความเหมาะสม; เครดิตราคาเป็น caption แยกจากชื่อรุ่น รองรับการเลื่อนตารางด้วย keyboard บนจอแคบ
- **Focus / motion / safe area:** route focus รอ lazy content, ไม่แย่ง focus จาก query inputs/Quiz/specs/dialogs; search focus อยู่ใน touch gesture; JS/CSS เคารพ reduced motion; รวม header/bottom-nav/tray offsets และเพิ่ม safe-area ให้ lightbox

Homepage, Catalog, Detail, Brands, Quiz และ Wishlist ได้รับ shared styling เหล่านี้ผ่าน components เดิม โครงสร้าง Hero/sections ของ Homepage ยังรอการออกแบบใน Phase C

## ผลทดสอบ

| ตรวจสอบ | ผล / หลักฐาน |
|---|---|
| `npm run build` | ผ่าน — [log](logs/build.txt) |
| `npm run catalog:check` | ผ่าน — 200รุ่น / 10แบรนด์ / แบรนด์ละ20 / ไม่มี ID หรือรุ่นซ้ำ — [log](logs/catalog-check.txt) |
| `npm run images:check` | ผ่าน — image files/registries/metadata ตรงกัน; 197รุ่นยังใช้ Placeholder — [log](logs/images-check.txt) |
| Price filter regression | **22/22** — URLสูงกว่า catalog max,0,invalid/reversed bounds, inclusive prices, unknown prices, reset, facets/sort/page, slider finite/unbounded endpoint — [log](logs/catalog-price.txt) |
| Scroll / focus helpers | **6/6** — reduced motion, synchronous search focus, placement/defaults และ guards — [log](logs/scroll-focus.txt) |
| Existing Pacifica regression | **79/79** — Gallery4ภาพ,3สี,lightbox,touch,source/data trust,ราคา,Compare/Wishlist,archived routes,Back/Forward — [ผล](regression/browser-phase-b.json) |
| Browser acceptance | **18/18** — Search/filters/sort/pagination/history, hover clipping, computed contrast, keyboard/touch menus, route/search focus, Wishlist persistence,Compare2–4/duplicates/remove/clear,Quiz5ขั้น/แก้คำตอบ/ผลลัพธ์ — [ผล](acceptance-final.json) |
| Category geometry / Thai words | **5/5** — 1440/1024/768/390/320px, icon centers,44px targets,คำไม่ถูกแบ่งกลางคำ,filter/history — [ผล](category-layout.json) |
| Responsive capture | **53มุมมอง**,36ภาพ — 1440×1000,1024×768,768×1024,390×844,320×740; ไม่พบ page overflow,visible broken images,console/runtime errors หรือ failed requests — [ผล](after/measurements.json) |
| Data / image preservation | SHA-256 ตรงกับ baseline ทั้ง **25ไฟล์** — [หลักฐาน](data-image-integrity.json) |

ทดสอบกับ Production Preview ที่พอร์ต5201ด้วย Chromium บน Linux และ touch emulation **ยังไม่ได้ทดสอบ Safari หรือ iPad เครื่องจริง** ไม่มีการอ้างว่าเป็นการรับรอง WCAG ทั้งเว็บไซต์

Compare same-value note ที่วัดได้หลังปรับมี contrastประมาณ6.65:1 แทนค่าก่อนปรับประมาณ2.72:1; hover probe ตรวจขอบเขตภาพที่วาดจริงไม่ให้ถูก ancestor ตัด ไม่ใช้เพียงตรวจชื่อ CSS class

Early runs พบข้อผิดพลาดใน test harness: การกด picker ก่อน debounce เสร็จ, การวัด route ก่อน lazy h1พร้อม, การ focus เมนูขณะยัง inert, และการรอภาพในแถบที่ถูกซ่อนด้วย opacity นอกจากนี้มีรอบที่ถูกขัดจังหวะจนเกิด BrokenPipe ปรับ harness ให้รอ UI จริงและเก็บ diagnostic reports ไว้ใน `diagnostics/` และ `failures/`; ผลปัจจุบันอยู่ในไฟล์ final ที่ลิงก์ด้านบน ไม่ใช้ผลรอบที่ไม่สมบูรณ์อ้างว่าผ่าน

## Performance ที่วัดจริง

Production Preview / Chromium บน Linux, browser context ใหม่ต่อหน้า, ไม่ throttle, สังเกต2.8วินาทีหลัง load จำนวน14ตัวอย่าง (7routes×2viewports) ไม่เปิด browser suites อื่นพร้อมรอบนี้ **ไม่ใช่ Lighthouse, field Core Web Vitals หรือการรับรองความเร็วบน Safari**

| Route / viewport | CLS Before | CLS After | LCP After (ms) |
|---|---:|---:|---:|
| home / 1440px | 0.00013 | 0.00021 | 1588 |
| catalog / 1440px | 0.23611 | 0.00018 | 828 |
| detail / 1440px | 0.23611 | 0.00018 | 1568 |
| brands / 1440px | 0.14587 | 0.00035 | 692 |
| compare / 1440px | 0.04733 | 0.00035 | 1484 |
| quiz / 1440px | 0.02449 | 0.00437 | 840 |
| wishlist / 1440px | 0.02381 | 0.00492 | 644 |
| home / 390px | 0.00021 | 0.00050 | 660 |
| catalog / 390px | 0.00002 | 0.00028 | 676 |
| detail / 390px | 0.00002 | 0.00028 | 1444 |
| brands / 390px | 0.00002 | 0.00028 | 580 |
| compare / 390px | 0.01408 | 0.02340 | 560 |
| quiz / 390px | 0.00002 | 0.00028 | 512 |
| wishlist / 390px | 0.00002 | 0.00026 | 540 |

Catalog/Detail Desktop ที่เคยมี Footer shift ประมาณ0.23611 ลดเหลือ0.00018 ในรอบนี้ ขณะที่ Compare Mobile เพิ่มจาก0.01408เป็น0.02340 จึงไม่ได้สรุปว่าทุกหน้ามีค่าดีขึ้นทั้งหมด ช่วง LCP ที่สังเกตหลังแก้512–1588ms เป็นค่าท้องถิ่นเท่านั้น

CSS gzip จาก17,992เป็น19,521ไบต์ (+1,529ไบต์) แลกกับ tokens และ shared styles; ไม่มี dependency, font หรือไฟล์ภาพใหม่ Catalog loading architecture ยังเหมือนเดิม ดู [ผลดิบ After](performance/after.json) และ [Baseline](../audit/performance/baseline.json)

## ข้อมูลที่รักษาไว้ / ข้อจำกัด

- ไม่เปลี่ยน Guitar ID, ข้อมูล200รุ่น, quota10×20, archived records, รูปภาพ, provenance/rights metadata, ราคา/สเปก/source.fields หรือสูตร Quiz
- ทุกรุ่นยังมีสถานะ partial ตามหลักฐานเดิม; 199รุ่นยังไม่มีราคาที่เผยแพร่ได้ และ197รุ่นไม่มีภาพจริงที่ลงทะเบียน จึงคงข้อความและ Placeholderเดิม ไม่เติมข้อมูลเพื่อความสวยงาม
- มี rights-documented photos2รุ่น และ project artwork Pacifica4ภาพ (รวมเป็น3รุ่นที่มีภาพ) การตรวจภาพผ่านไม่ได้แปลว่าทุกรุ่นมีรูปถ่าย
- ไม่เพิ่ม dependencies; package/lockfiles, Router และ ShopContext ไม่เปลี่ยน
- Safari/iPad จริง รวม fullscreen/notch safe-area, software keyboard และ assistive technology ยังต้องตรวจบนอุปกรณ์จริง ผล Chromium ไม่ใช้แทนผลดังกล่าว
- Phase C และการเปลี่ยน composition ของ Homepage ยังรอผู้ใช้ตรวจ/อนุมัติ

## ไฟล์โปรแกรมที่แก้ / เพิ่ม (30ไฟล์)

- [`src/components/catalog/ActiveFilters.jsx`](../../../src/components/catalog/ActiveFilters.jsx)
- [`src/components/catalog/CatalogCard.jsx`](../../../src/components/catalog/CatalogCard.jsx)
- [`src/components/catalog/CategoryNavigation.jsx`](../../../src/components/catalog/CategoryNavigation.jsx)
- [`src/components/catalog/PriceRange.jsx`](../../../src/components/catalog/PriceRange.jsx)
- [`src/components/compare/CompareTable.jsx`](../../../src/components/compare/CompareTable.jsx)
- [`src/components/detail/ImageLightbox.jsx`](../../../src/components/detail/ImageLightbox.jsx)
- [`src/components/detail/StickyGuitarBar.jsx`](../../../src/components/detail/StickyGuitarBar.jsx)
- [`src/components/guitar/GuitarCard.jsx`](../../../src/components/guitar/GuitarCard.jsx)
- [`src/components/layout/BottomBar.jsx`](../../../src/components/layout/BottomBar.jsx)
- [`src/components/layout/CompareBar.jsx`](../../../src/components/layout/CompareBar.jsx)
- [`src/components/layout/Footer.jsx`](../../../src/components/layout/Footer.jsx)
- [`src/components/layout/IconButton.jsx`](../../../src/components/layout/IconButton.jsx)
- [`src/components/layout/Logo.jsx`](../../../src/components/layout/Logo.jsx)
- [`src/components/layout/MegaMenu.jsx`](../../../src/components/layout/MegaMenu.jsx)
- [`src/components/layout/MobileMenu.jsx`](../../../src/components/layout/MobileMenu.jsx)
- [`src/components/layout/Navbar.jsx`](../../../src/components/layout/Navbar.jsx)
- [`src/components/layout/ScrollManager.jsx`](../../../src/components/layout/ScrollManager.jsx)
- [`src/components/ui/Button.jsx`](../../../src/components/ui/Button.jsx)
- [`src/components/ui/DiscoveryRoute.jsx`](../../../src/components/ui/DiscoveryRoute.jsx)
- [`src/components/ui/SectionHeading.jsx`](../../../src/components/ui/SectionHeading.jsx)
- [`src/hooks/useCatalogFilters.js`](../../../src/hooks/useCatalogFilters.js)
- [`src/hooks/useSearchNavigation.js`](../../../src/hooks/useSearchNavigation.js)
- [`src/i18n/en.js`](../../../src/i18n/en.js)
- [`src/i18n/th.js`](../../../src/i18n/th.js)
- [`src/index.css`](../../../src/index.css)
- [`src/main.jsx`](../../../src/main.jsx)
- [`src/styles/polish.css`](../../../src/styles/polish.css)
- [`src/utils/dom.js`](../../../src/utils/dom.js)
- [`tailwind.config.js`](../../../tailwind.config.js)
- [`src/styles/tokens.css`](../../../src/styles/tokens.css)

เอกสารและเครื่องมือทดสอบเพิ่มเติมอยู่ในโฟลเดอร์นี้ พร้อม [คำสั่งทดสอบ](tests/README.md),ภาพ Before เดิมอยู่ใน `../audit/before/` และ Styleboard ที่อนุมัติอยู่ใน `../proposals/`

## อัปเดต Codespaces บน iPad

เปิด Codespace เดิมจาก https://github.com/codespaces แล้วรันใน Terminal:

```sh
cd /workspaces/fretline
git pull --ff-only origin master
npm install
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

เปิดแท็บ **Ports → 5173 → Open in Browser (รูปโลก)** ใน Safari ต้องเปิด Codespace และให้ Vite ยังทำงานอยู่ URL ของเว็บใช้ Forwarded Address ของ Codespaceนั้น ไม่ใช่ `localhost` ของ iPad

หาก `git pull` แจ้งว่ามีไฟล์แก้ค้าง ให้เก็บงานเดิมก่อนด้วย `git stash push -u -m "backup-before-phase-b"` แล้วจึง pull ห้ามใช้ reset/force เพื่อลบงานเดิม หากมี process ใช้5173อยู่แล้ว ให้หยุด processเดิมใน Terminalนั้นด้วย Ctrl+Cก่อนเริ่มใหม่
