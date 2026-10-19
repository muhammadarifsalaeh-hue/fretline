# Fretline — Phase 3: Catalog & Guitar Detail

พัฒนาต่อจาก commit `f74f79c` ในโปรเจกต์เดิม `/workspace/fretline`.
ขอบเขตรอบนี้คือ Catalog และ Guitar Detail เท่านั้น ยังไม่เริ่ม Phase 4.
ไม่มีการเพิ่ม dependency, backend, database หรือบริการภายนอก.

## สิ่งที่พัฒนา

### Catalog

- ปรับหัวหน้า ค้นหา หมวดหมู่ Sidebar และการ์ดเป็นโทนดำ–ทองตามภาพอ้างอิง
  โดยใช้ฟอนต์ไทยและ design tokens เดิม
- Search กรองข้อมูลจริงใน static catalog ขณะพิมพ์ กด Enter หรือปุ่มค้นหาเพื่อ
  ย้าย focus ไปผลลัพธ์ มีปุ่มล้างคำค้น
- Category Navigation มีไอคอนตามประเภทที่มีจริง และแสดงสถานะเลือกได้หลายประเภท
- Sidebar ใช้ FilterPanel เดิมร่วมกับ drawer บนมือถือ เพิ่มการค้นหาแบรนด์
  และสถานะไม่พบแบรนด์ รักษา checkbox, จำนวนผลลัพธ์, slider สองหัว และ preset ราคา
- Pagination 9 รุ่นต่อหน้า มีเลขหน้า ปุ่มก่อน/ถัดไป สถานะหน้าปัจจุบัน
  เก็บหน้าใน URL, reload และ Browser Back ได้ เปลี่ยนตัวกรองแล้วกลับหน้าแรก
- แก้การอ่านค่าราคา `max=0`, ค่าที่ไม่ใช่ตัวเลข และเลขหน้าเกินจำนวนผลลัพธ์
  รุ่นที่ไม่ทราบราคายังถูกยกเว้นเมื่อใช้ตัวกรองราคา
- การ์ดมีภาพ/ภาพสำรอง ชื่อ ประเภท แบรนด์ ราคา สถานะข้อมูล รายละเอียด
  Wishlist และ Compare โดยใช้ ShopContext และ localStorage เดิม
- กริด 1/2/3 คอลัมน์ตามพื้นที่หน้าจอ ปรับการ์ดให้กระชับเฉพาะ Catalog
- แยก Catalog และ Detail เป็น lazy route chunks พร้อม Suspense skeleton
  ระหว่างโหลดจริง และ Error Boundary พร้อมลองใหม่เมื่อโหลดหน้าล้มเหลว
  ไม่สร้าง delay หรือจำลอง backend ขึ้นมา

### Guitar Detail

- ปรับสัดส่วน Gallery/ข้อมูลหลัก ระยะห่าง ปุ่ม และ border ตามภาพอ้างอิง
- Thumbnail rail แนวตั้งบนจอที่กว้างพอ และแนวนอนบนมือถือ
  เลือกรูป เปลี่ยนด้วยปุ่ม/การปัด ซูมด้วยเมาส์ และเปิด Lightbox ได้
- โหลดภาพหลักเฉพาะรูปที่เลือก ไม่ mount ภาพขนาดใหญ่ทุกมุมพร้อมกัน
  รูปที่โหลดไม่ได้มี fallback และเลือกรูปที่ถูกต้องต่อได้
- Lightbox trap focus, ใช้ลูกศร/Escape และคืน focus กลับปุ่มเปิด
- เพิ่มแท็บ รายละเอียด/สเปก/รีวิว พร้อมความสัมพันธ์ ARIA, roving tabindex,
  ArrowLeft/ArrowRight/Home/End และ tab panels ที่มีชื่อ
- ตารางสเปกใช้ semantic table แบ่งกลุ่ม และแสดงช่องที่ไม่ทราบเป็น “ไม่ระบุ”
- รักษาลิงก์ตรง `#specs`, สีที่เลือกได้, sticky summary, source information,
  รายการใกล้เคียง และปุ่ม Wishlist/Compare เดิม
- ลบการนำคะแนน/จำนวนรีวิวตัวอย่างมาแสดงบน Detail แท็บรีวิวระบุชัดว่า
  ยังไม่มีรีวิวที่ตรวจสอบแล้ว ไม่สร้างดาว คะแนน จำนวนรีวิว หรือเนื้อหารีวิวใหม่
- ราคาตัวอย่างมีป้ายกำกับติดกับราคา รุ่นไม่มีราคาแสดง “สอบถามราคา”
  สถานะและลิงก์แหล่งข้อมูลยังคงแสดงอยู่

## การคงฟีเจอร์เดิม

Homepage และ components ใน `src/components/home/` ไม่ได้แก้ดีไซน์.
ระบบไทย/อังกฤษ, แบรนด์, Wishlist, Compare, Quiz, 404, import/check scripts,
ข้อมูล 36 รุ่น และแหล่งข้อมูลเดิมยังอยู่ครบ ไม่มีการเติมราคา/สเปก/รูปจริงขึ้นมาเอง.
เพิ่มเพียง class สำหรับจัดสีภาพสำรองใน Catalog/Detail โดยไม่เปลี่ยนหน้าตา Homepage.

## Files modified / added

- `src/App.jsx`: lazy routes และ DiscoveryRoute boundary
- `src/pages/CatalogPage.jsx`, `src/pages/GuitarDetailPage.jsx`
- `src/hooks/useCatalogFilters.js`, ใหม่ `src/hooks/useDialogFocus.js`
- `src/components/catalog/`: CatalogCard, CatalogToolbar, FilterGroup,
  FilterPanel, MobileFilterDrawer, PriceRange และเพิ่ม CategoryNavigation,
  CatalogPagination
- `src/components/detail/`: GuitarGallery, ImageLightbox, SpecTable และเพิ่ม DetailTabs
- ใหม่ `src/components/ui/DiscoveryRoute.jsx`
- `src/components/guitar/ImagePlaceholder.jsx`: เพิ่ม class สำหรับจัดสไตล์เฉพาะหน้า
- `src/index.css`, `src/i18n/th.js`, `src/i18n/en.js`
- `README.md`, รายงานนี้ และหลักฐานใน `docs/qa-phase3/`

## Tests performed

- `npm run build`: ผ่าน ดูขนาดไฟล์/เวลาจริงใน `docs/qa-phase3/build.txt`
- `npm run catalog:check`: ผ่าน ไม่มีปัญหาโครงสร้างข้อมูล
- `npm run images:check`: exit 0 แต่ยังรายงาน **ไม่มีรูปจริง 0/36 รุ่น**
  การรันสคริปต์สำเร็จไม่ได้หมายความว่ามีภาพครบ
- Production browser suite: **64/64 assertions ผ่าน** ครอบคลุม Search,
  Search submit, ประเภท/แบรนด์/ราคา, Sorting, Pagination, invalid URLs,
  reload/Back, Empty/Clear, Wishlist/Compare/persistence, Detail tabs,
  การไม่แสดงรีวิวตัวอย่าง, Source/unknown values, 404, drawer/focus,
  reduced motion และหน้าแรก
- ตรวจ Catalog และ Detail ที่ 320, 390, 768, 1024 และ 1440px:
  ไม่พบ document horizontal overflow
- Normal interaction run ไม่พบ JavaScript page error, console error หรือ
  failed request ส่วน fault injection จงใจหยุด lazy chunk เพื่อทดสอบ
  Loading → Error → Retry recovery แยกต่างหาก
- Gallery suite: **13/13 assertions ผ่าน** ใช้ SVG test patterns เฉพาะใน
  หน่วยความจำของเบราว์เซอร์ทดสอบ ตรวจ thumbnail, Lightbox, keyboard,
  focus trap/restore, simulated touch swipe, broken image fallback/recovery
  ไม่ได้เพิ่มรูปหรือข้อมูลทดสอบลงใน production catalog
- หลังเพิ่มการรักษา `#specs` มี final smoke และ recapture screenshots จาก
  build ล่าสุด **5/5 assertions ผ่าน** ผลแยกใน `final-smoke-results.json`
- `git diff --check`: ผ่าน

ผลแบบ machine-readable และสคริปต์ทดสอบอยู่ใน `docs/qa-phase3/`.
Browser suite ใช้ Chromium/Playwright ที่มีในสภาพแวดล้อม ไม่ได้เพิ่มลง dependencies ของแอป.

## Screenshots

ใน `docs/qa-phase3/` มี Catalog และ Detail ที่ Desktop 1440px,
Tablet 768px, Mobile 390px รวมภาพเต็มหน้าบน Desktop.
ภาพทั้งหมดมาจากหน้าจริง ไม่มีการใส่ภาพสินค้าใน screenshot แทนข้อมูลที่ขาด.
มีภาพ Homepage สำหรับตรวจ regression ด้วย.
เปรียบเทียบกับ reference ด้วยสายตา ไม่ได้อ้าง pixel-diff score.

## Performance / accessibility

- Entry JS ลดจากประมาณ 361 KB ใน Phase 2 เหลือประมาณ 335 KB โดยเลื่อน
  Catalog/Detail ไปโหลดตาม route ขนาดรวมของทั้งแอปยังขึ้นกับฟีเจอร์ใหม่
  ตัวเลข gzip และ chunk จริงอยู่ใน build log ไม่มีการอ้าง Lighthouse score
- รูปจริงยังใช้ lazy loading ตามเดิม ภาพหลักที่เลือกใน Gallery ได้ priority
- ใช้ semantic landmarks/table, ชื่อ controls, aria-current/pressed/selected,
  keyboard tabs, modal focus management, reduced motion และ spacing ภาษาไทยเดิม
- ไม่ได้อ้างว่าผ่าน accessibility audit ทั้งระบบ, Safari/Firefox หรือ physical devices

## Remaining issues

1. ยังไม่มีภาพจริงที่ตรงรุ่นทั้ง 36 รุ่น การแสดง Gallery จริงบนข้อมูล production
   ต้องใส่ภาพที่มีสิทธิ์ใช้ผ่านระบบเดิม ห้ามใช้ภาพ Hero/AI แทนรุ่นสินค้า
2. มีข้อมูลตัวอย่าง 18 รุ่น และข้อมูลตรวจบางส่วน 18 รุ่น ไม่มีรุ่นที่ยืนยันครบ
   ราคาที่ไม่ทราบ 18 รุ่นยังไม่ถูกเดา การตรวจข้อมูลผู้ผลิตใหม่ยังเป็นงานเนื้อหาต่อไป
3. ความเหมือน reference ถูกจำกัดด้วยภาพที่ขาดและข้อมูลเดิม ไม่อ้างว่าเหมือนทุกพิกเซล
4. ข้อความรายละเอียดที่นำเข้าบางส่วนยังเป็นภาษาอังกฤษ เก็บข้อความแหล่งเดิมไว้
5. Phase 4 และการตรวจข้ามเบราว์เซอร์/อุปกรณ์จริงยังไม่ได้ทำ

## Delivery / next step

ส่ง source, build `dist/`, screenshots, reports, commit metadata และ patch
ใน ZIP ล่าสุด โดยไม่รวม node_modules/.git. บันทึก Phase 3 เป็น commit แยก
จาก `f74f79c`. **หยุดที่ Phase 3 และรอคำสั่งก่อนเริ่ม Phase 4.**
