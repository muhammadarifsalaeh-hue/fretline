# Fretline — Phase 5: Brands & Wishlist

พัฒนาต่อใน `/workspace/fretline` บน `master` จาก `b735a821fb96f1132b13a66e27cf22e36ff07304` โดยรักษาประวัติ Phase 1–4 รวมถึง `f74f79c`, `c8b1bf3` และ `bb4a759` ไม่มีการสร้างโปรเจกต์ใหม่ เพิ่ม Dependencies หรือเริ่ม Phase 6

Repository: https://github.com/muhammadarifsalaeh-hue/fretline

## 1. Files modified / added

| ไฟล์ | สิ่งที่เปลี่ยน |
| --- | --- |
| `src/pages/BrandsPage.jsx` | หน้า Brands ภาษาไทย พร้อม Search, URL filters, Sorting และ Empty State |
| `src/components/brands/BrandCard.jsx` | การ์ดชื่อแบรนด์แบบกระชับตาม Reference แสดงจำนวนรุ่นจริงใน Catalog |
| `src/components/brands/BrandsToolbar.jsx` | Search, ประเภทกีตาร์, ประเทศเดิมที่ระบุว่ารอยืนยัน, Sorting และ Clear Filters |
| `src/pages/BrandDetailPage.jsx` | รายการรุ่นของแบรนด์, ประเภท, Sorting, แหล่งข้อมูลรุ่น, Empty และ Unknown Brand State |
| `src/pages/WishlistPage.jsx` | รายการแนวนอน, Sorting ใน URL, ล้างรายการพร้อมยืนยัน และส่งรายการไป Compare |
| `src/components/wishlist/WishlistRow.jsx` (ใหม่) | รูป/ภาพประกอบ, ข้อมูลรุ่น, ลิงก์แบรนด์/รายละเอียด, Remove และ Compare |
| `src/components/ui/DiscoveryHeading.jsx` (ใหม่) | Heading และ Breadcrumb ที่ใช้ร่วมกันในทั้งสามหน้า |
| `src/components/ui/SortSelect.jsx` (ใหม่) | Native select ที่มี Label และ Keyboard Support |
| `src/components/ui/ConfirmDialog.jsx` | เพิ่มข้อความยืนยันที่กำหนดได้ โดยรักษาค่าตั้งต้นของ Phase 4 |
| `src/components/catalog/CatalogCard.jsx` | เพิ่มตัวเลือก `verifiedOnly` สำหรับ Brand Detail โดยคงค่าเริ่มต้นของ Catalog เดิม |
| `src/data/brands.js` | คำนวณจำนวน/ประเภทจาก Catalog, นับรุ่นที่มีแหล่งข้อมูล และตัดราคาตัวอย่างออกจากช่วงราคาแบรนด์ |
| `src/utils/brandFilters.js` | แปลข้อความเรียงลำดับเป็นไทย/อังกฤษ |
| `src/utils/guitarSort.js` | เพิ่มการเรียงด้วยราคาที่มีแหล่งอ้างอิง รุ่นที่ไม่ทราบราคาอยู่ท้ายเสมอ |
| `src/i18n/th.js`, `src/i18n/en.js` | ข้อความ Phase 5 และสถานะข้อมูลทั้งสองภาษา |
| `src/index.css` | Styles ที่จำกัดขอบเขตใน Phase 5 พร้อม Responsive และ Focus States |
| `src/App.jsx` | Lazy-load ทั้งสามหน้าและใช้ Loading/Error Boundary เดิม |
| `scripts/check-phase5.mjs` (ใหม่), `package.json` | เพิ่ม `npm run phase5:check` โดยไม่เพิ่มแพ็กเกจ |
| `README.md`, `docs/PHASE_5_REPORT.md` | รายงานและลิงก์ส่งมอบ |
| `docs/qa-phase5/` (ใหม่) | Browser scripts, ผลตรวจ JSON, Logs และ Screenshots |

ไฟล์ Homepage, Catalog Page, Guitar Detail Page, Compare Page, Quiz และ ShopContext ไม่ถูกแก้ไข ฟังก์ชัน Wishlist ยังใช้ `fretline:wishlist` และ Compare ใช้ `fretline:compare` ผ่าน Context เดิม ไม่มี state รายการซ้ำอีกชุด

## 2. Features implemented

- **Brands:** กริดโทนดำ–ทอง แสดง 11 แบรนด์ / 36 รุ่นจาก Catalog จริง Search ไม่สนตัวพิมพ์เล็ก–ใหญ่ รองรับ Filter, Sorting, URL และ Back/Forward
- **ชื่อและโลโก้:** ใช้ชื่อแบรนด์ด้วยตัวอักษรปกติ ยังไม่มีไฟล์โลโก้ที่ได้รับอนุญาต จึงไม่วาดหรือสร้างโลโก้ขึ้นใหม่
- **Brand Detail:** แสดงเฉพาะรุ่นของแบรนด์นั้น มีตัวกรองประเภท เรียงลำดับ ลิงก์เข้า Catalog ที่กรองแบรนด์ไว้ และลิงก์ไป Guitar Detail, Compare และ Wishlist ผ่านการ์ดเดิม
- **ความน่าเชื่อถือ:** แสดงจำนวนรุ่นที่มีแหล่งอ้างอิงแยกจากจำนวนรุ่นทั้งหมด พร้อม URL/วันที่ที่บันทึกไว้ ไม่เพิ่มประวัติแบรนด์ที่ไม่มีแหล่งข้อมูล
- **Wishlist:** แสดงรุ่นที่บันทึกล่าสุดก่อน เปลี่ยน Sorting ได้ เปิดรายละเอียดหรือแบรนด์ของรุ่นนั้นได้ ลบทีละรุ่นหรือยืนยันล้างทั้งหมด และส่งสูงสุด 4 รุ่นแรกตามลำดับที่แสดงไป Compare
- **การแทน Compare:** ขอการยืนยันก่อนแทนรายการ Compare เดิมที่แตกต่างกัน ปุ่มรายรุ่นแสดงสถานะที่เลือกแล้วและปิดการเพิ่มเมื่อครบ 4 รุ่น
- **Accessibility:** Native buttons/selects, `aria-pressed`, Live Count, Dialog Focus Trap, Escape เพื่อยกเลิก และย้าย Focus ไปตำแหน่งที่ใช้งานต่อได้หลังลบรายการ
- **Performance:** แยก JavaScript ของทั้งสามหน้าโหลดเมื่อเปิด Route ใช้ภาพและ Context เดิม ไม่เพิ่ม Dependencies

## 3. Bugs / data presentation fixed

- เลิกใช้ราคาตัวอย่างคำนวณช่วงราคาแบรนด์และยอดรวม Wishlist
- Brand Detail และ Wishlist ไม่แสดงจำนวนเงินหรือราคาเดิมที่ยังไม่มีแหล่งอ้างอิง
- Brand Detail ไม่แสดงปีก่อตั้ง/ประเทศเดิมเป็นประวัติที่ยืนยันแล้ว ตัวกรองประเทศเดิมยังใช้งานได้พร้อมข้อความว่ารอยืนยัน
- URL แบรนด์ที่ไม่พบ รวมถึง `__proto__` และ `constructor` ไม่ถูกอ่านเป็นแบรนด์ผ่าน Object prototype
- ปุ่มล้าง Wishlist เดิมที่ต้องแตะซ้ำภายในเวลาจำกัด เปลี่ยนเป็น Dialog ยืนยันที่ใช้คีย์บอร์ดได้
- เก็บ Sorting/Filters ใน URL เพื่อให้ Back/Forward คืนค่าหน้าได้
- ระบบ normalize ของ Phase 4 ยังคัดรหัสซ้ำ/รหัสเก่าออกจาก Local Storage โดยรักษารุ่นที่ยังมีอยู่

## 4. Tests performed

ตรวจจริงด้วย Vite Production Build และ Chromium ผ่าน Python Playwright ไม่มีการเพิ่ม Browser Dependency ในโปรเจกต์

| การทดสอบ | ผล |
| --- | --- |
| `npm run build` | ผ่าน — 149 modules, แยก Route chunks ของทั้งสามหน้า |
| `npm run catalog:check` | ผ่านการตรวจโครงสร้าง — 36 รุ่น, 11 แบรนด์; 18 sample / 18 partial / 0 fully verified |
| `npm run images:check` | Exit 0 แต่ภาพจริงยังไม่ครบ: **0/36 รุ่น** ใช้ภาพประกอบที่ระบุสถานะ |
| `npm run phase5:check` | 15/15 ผ่าน — Counts, Category Membership, Brand Lookup, Filters, Price Trust, Sorting, Deduplication และภาษา |
| `npm run phase4:check` | 19/19 ผ่าน — สูตรคะแนน Quiz, Compare Rows, Source Trust และ Shared IDs เดิม |
| Production Browser QA | 80/80 ผ่าน — Search/Filter/Sort, Unknown/Empty States, Wishlist ข้ามหน้า, Persistence, Clear, Compare 4 รุ่น และ Route Smoke ของ Phase 1–4 |
| Development / Strict Mode QA | 11/11 ผ่าน — Wishlist-to-Compare URL, Reload, Removal, ภาษาอังกฤษ และ Local Storage ถูกปิดใช้งาน |
| Responsive interaction QA | 17/17 ผ่าน — Search/Keyboard Navigation, Brand Detail Filter/Sort, Brand Catalog Link และ Back ที่ Desktop/Tablet/Mobile |
| Console / Runtime | ไม่พบ Error ในชุด Browser ทั้งสามชุด |
| Network requests | ชุด Production Browser หลักไม่พบ Request ล้มเหลว |
| Responsive | ตรวจ 320, 390, 768, 1024 และ 1440px ไม่พบ Document ล้นแนวนอนในหน้าที่พัฒนา |

ผลรวม **142 checks ผ่าน** (108 Browser + 34 Logic/Regression) นอกเหนือจาก Build และ Data Checks รายละเอียดรายข้ออยู่ใน JSON และ Logs ใน `qa-phase5/`

การทดสอบรอบแรกมี Locator ของ Automation ไม่ตรงกับชื่อปุ่มเดิมใน Guitar Detail และ Page Size ของ Catalog แก้ตัวทดสอบให้ตรงกับ UI จริงก่อนรันซ้ำ ผลข้างต้นเป็นผลรอบสุดท้าย ไม่มีการเปลี่ยนปุ่มหรือ Pagination เดิมเพื่อให้เทสต์ผ่าน

### Screenshots

| หน้า | Desktop | Tablet | Mobile |
| --- | --- | --- | --- |
| Brands | [ภาพ](qa-phase5/brands-desktop.png) | [ภาพ](qa-phase5/brands-tablet.png) | [ภาพ](qa-phase5/brands-mobile.png) |
| Brand Detail | [ภาพ](qa-phase5/brand-detail-desktop.png) | [ภาพ](qa-phase5/brand-detail-tablet.png) | [ภาพ](qa-phase5/brand-detail-mobile.png) |
| Wishlist | [ภาพ](qa-phase5/wishlist-desktop.png) | [ภาพ](qa-phase5/wishlist-tablet.png) | [ภาพ](qa-phase5/wishlist-mobile.png) |
| Empty Wishlist | — | — | [ภาพ](qa-phase5/wishlist-empty-mobile.png) |

ใช้ Reference ที่แนบในบทสนทนาและ Design System ของ Phase 1–4 ตรวจดูภาพที่จับจริงด้วยสายตา ไม่มีการอ้างผล Pixel Diff ภาพสินค้าจริงและโลโก้จึงยังแตกต่างจาก Reference

## 5. Remaining issues / verification limits

1. Catalog ยังมี 18 รุ่นตัวอย่างและ 18 รุ่นที่ตรวจบางส่วน ยังไม่มีรุ่นที่ตรวจครบทุกฟิลด์ ไม่มีการเพิ่มราคา/สเปก/รีวิวสมมติใน Phase 5
2. ยังไม่มีภาพกีตาร์จริงทั้ง 36 รุ่นหรือโลโก้แบรนด์ที่ได้รับอนุญาต จึงใช้ภาพประกอบ/ชื่อแบรนด์ และระบุว่าไม่ใช่ภาพรุ่นจริง
3. ยังไม่มีประวัติแบรนด์ที่บันทึกแหล่งอ้างอิง ประเทศและปีก่อตั้งเดิมยังเก็บไว้เพื่อรักษาระบบเดิม หน้า Brand Detail ไม่ใช้เป็นประวัติยืนยัน Homepage ไม่ถูกเปลี่ยนใน Phase นี้
4. URL/วันที่อ้างอิงใน Brand Detail มาจากข้อมูลที่บันทึกไว้ใน Catalog ไม่ได้อ้างว่ามีการตรวจเว็บไซต์ผู้ผลิตซ้ำหรือยืนยันทุกช่องใน Phase นี้
5. ไม่มีราคาที่มีแหล่งอ้างอิงใน Catalog ปัจจุบัน ตัวเลือกเรียงราคาจึงอธิบายสถานะและเรียงแบบมีลำดับคงที่ ไม่ใช้ราคาตัวอย่าง
6. ทดสอบ Browser จริงด้วย Chromium และขนาดหน้าจอจำลอง ยังไม่ได้ทดสอบ Safari/WebKit หรือ iPad เครื่องจริง
7. Wishlist บันทึกเฉพาะเบราว์เซอร์/โปรไฟล์ปัจจุบัน ไม่มี Backend หรือ Sync ข้ามอุปกรณ์ หาก Browser ปิด Local Storage ระบบยังใช้ในหน่วยความจำระหว่างเปลี่ยน Route ได้ แต่ไม่รับประกันการคงรายการหลังปิด/โหลดใหม่
8. ยังไม่ใช่ผลตรวจ Accessibility ด้วย Screen Reader หรือ Performance Benchmark แบบ Lighthouse

## 6. GitHub / Codespaces delivery

ส่ง Commit บน `master` ไป Repository เดิมด้วยการ Push ปกติ ตรวจ Remote ก่อน Push ห้าม Force Push และไม่แก้ประวัติเก่า Commit Hash ส่งมอบอยู่ในข้อความส่งงานและ `review/delivery.json` ใน ZIP

เปิด Codespaces เดิมจาก GitHub → **Code → Codespaces** โดยใช้บัญชีที่มีสิทธิ์เข้าถึง Private Repository จากนั้นบันทึกงานที่แก้เอง และหยุด Vite เดิมด้วย `Ctrl+C` ก่อนใช้คำสั่ง:

```bash
git status
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

เปิดแท็บ **Ports → 5173 → Open in Browser** แล้วเปิด URL นั้นใน Safari ของ iPad ด้วยบัญชี GitHub เดียวกัน รักษา Port Visibility เป็น **Private**

หาก `git pull --ff-only` แจ้งว่ามีงานในเครื่องหรือ Branch แยกจาก Remote ให้รักษางานนั้นและแก้สถานะ Git ก่อน ไม่ใช้ Reset/Force เพื่อทับงาน หาก Vite แจ้ง Blocked Host ให้เพิ่มเฉพาะชื่อ Host ของ URL ที่ Codespaces ส่งต่อไว้ใน `server.allowedHosts` ของ Vite โดยรักษา Plugins/Alias เดิม

หน้าที่ตรวจดู: `/brands`, `/brands/yamaha`, `/wishlist` ลองบันทึกกีตาร์จากหน้าอื่นก่อนเปิด Wishlist เพราะรายการในเครื่องที่ใช้ทดสอบไม่ได้ส่งไปยัง iPad

**หยุดหลัง Phase 5 และรอคำสั่งก่อน Phase 6**
