# Phase A — Complete Design Audit

Baseline: `82fbe9b` บนโปรเจกต์ Fretline เดิม Audit ก่อนเปลี่ยน implementation ภาพ Reference เดิมในบทสนทนาใช้ประกอบแนวทางดำ–ทอง/ลำดับหน้า ไม่ได้ทำ pixel-diff กับ Reference เพราะไม่มีไฟล์หน้าจอเดี่ยวที่ระบุ viewport ตรงกับภาพชุดทดสอบ

## ข้อสรุป

ควรเริ่มจากระบบ typography, control/card variants, readable text, fixed-layer geometry และ loading state ก่อนจัดหน้าใหม่ มีปัญหาฟังก์ชันและภาพที่ยืนยันได้ซึ่งควรแก้ร่วมกับ regression case ไม่ควรเพิ่ม stylesheet override อีกชั้นหรือปรับทุกหน้าพร้อมกัน

เว็บไซต์มีฐานที่ใช้ต่อได้: local fonts, source-qualified pricing, placeholders ที่ไม่ใช้รูปผิดรุ่น, URL filters, gallery/keyboard, modal focus/scroll lock, ShopContext และ Wishlist persistence ไม่จำเป็นต้องเพิ่ม dependency หรือเปลี่ยนข้อมูลสินค้าเพื่อทำดีไซน์ใหม่

## ปัญหาตามลำดับความสำคัญ

| Priority | ปัญหา | หลักฐาน / ผลกระทบ | แนวทางแก้ |
|---|---|---|---|
| **P1 — Function** | ตัวกรอง “มากกว่า ฿70k” คืน Pacifica ฿34,000 | **ยืนยันใน Chromium** URL `/guitars?min=70000` มีผลลัพธ์1รุ่นราคา34000 ขณะที่ไม่มีราคาที่ตรวจสอบแล้วเกิน70000 `PriceRange.jsx:6`, `useCatalogFilters.js:42,60` | แยก requested bounds ออกจาก known-price maximum และทดสอบ empty state/URL/Back/Forward โดยไม่แก้ราคาสินค้า |
| **P1 — Product image** | Hover ขยายภาพจนตัดขอบ | **ยืนยัน** `matrix(1.05,...)` ภาพ Catalog ถูกกรอบตัดด้านบนและล่างประมาณ6.49px แม้ `object-fit:contain` `CatalogCard.jsx:33,39`, `GuitarImage.jsx:36` | ใช้ surface/border feedback แทนการ scale full-bleed artwork ตรวจภาพเต็มทั้ง hover/focus/touch |
| **P1 — Loading / CLS** | Footer เคลื่อนระหว่าง loading กับหน้าจริง | Production sample ที่1440px พบ Catalog/Detail observed CLS≈0.23611; Catalogซ้ำอีก2ครั้ง≈0.23611 โดย LayoutShift source คือ `FOOTER` `DiscoveryRoute.jsx:9` ใช้ skeleton ความสูงต่างจากหน้าจริง | จัด loading geometry ให้ Footer ไม่โผล่แล้วกระโดดออกใน first viewport ใช้ skeleton ที่เหมาะกับ page role และวัดซ้ำ |
| **P1 — Readability** | ข้อมูล Compare ที่เหมือนกันจางเกินไป | Live computed color ของ label11pxเป็น `rgba(138,138,133,.6)` และ value12pxเป็น `rgba(245,245,242,.45)` `CompareTable.jsx:110,117`; คำนวณบน canvas≈2.72:1 / 4.21:1 ต่ำกว่า4.5:1ของข้อความปกติ | ใช้ secondary/muted tokens ที่อ่านได้ แยกด้วยน้ำหนัก/พื้นผิวแทนลด opacity |
| **P1 — Hierarchy** | หัวข้อและข้อมูลรองใช้หลายสเกล | Catalog, Brands/Wishlist, shared section heading และชื่อรุ่นมีระบบคนละชุด บางข้อความ9–11px; `index.css:17` บังคับ line-height/tracking ของ h1–h4ทุกภาษา | แยก Display/Page/Section/Product/Body/Caption และ Thai/English rules โดยคงระยะวรรณยุกต์ |
| **P1 — Motion / keyboard** | JS smooth scroll ไม่ดู reduced-motion และ route focus ไม่สม่ำเสมอ | พบจาก source `utils/dom.js:3`, `ScrollManager.jsx:12`, `BottomBar.jsx:15`, `Logo.jsx:9`; main มี tabIndex แล้วแต่ route managerยังไม่focus; Quizจัดfocusเองอยู่แล้ว | helper scroll ที่เคารพ preference + route-focus strategy ไม่แย่ง focus ของ Catalog query/Quiz |
| **P2 — Consistency** | Card และปุ่มแตกต่างตามหน้า | Homepage `GuitarCard` กับ `CatalogCard` ใช้สัดส่วนภาพ ขนาดชื่อ และการเผย action ต่างกัน; pill/rounded rectanglesหลายแบบ | Shared card spec ที่มี Editorial/Compact variants และ control roles ชัดเจน |
| **P2 — Density** | Featured desktop6ใบอัดชื่อรุ่นยาว | `FeaturedGuitars.jsx:103`, `index.css:154` ทำให้ชื่อรุ่นเหลือ18pxในคอลัมน์แคบ | ใน Homepage phase ทดลอง3–4 editorial cards/viewport โดยไม่เปลี่ยนจำนวนรุ่น |
| **P2 — Maintainability** | Tokens มีอยู่แต่ถูก bypass โดย hard-coded CSS | CSSหลัก588บรรทัด มี238 hex occurrences/71 literal values; polish129บรรทัดเพิ่ม25/16 รวม alpha variants ไม่ใช่71สีแบรนด์คนละสี | Consolidate semantic variables และ component styles เป็นกลุ่ม แทนเพิ่ม override sheet |
| **P2 — Touch** | บาง control มีพื้นที่กดเล็ก | Slider22px, price presets36px; breadcrumbsและข้อมูลรองบางส่วนต่ำกว่า44px เป้าหมาย44pxเป็นแนวทางสำหรับtouch ไม่ถือว่าทุกลิงก์เล็กเป็น WCAG failure | ขยาย hit area และใช้44/48px control roles โดยไม่ทำให้ UI หนัก |
| **P2 — Fixed geometry** | Header/BottomBar/CompareTray/StickyBar ใช้ offset แยกกัน | Sourceใช้64/80/60/68pxคนละจุด; probeที่320/390/768pxพร้อมcompare2รุ่นยังไม่พบ fixed rectangles ทับกัน | รวม height/layer/safe-area tokens เพื่อป้องกัน regression ไม่รายงานว่าเป็น overlap ที่พบแล้ว |
| **P2 — SEO** | Metadata ส่วนใหญ่เป็นค่าเดียวทั้งเว็บ | 14 production samplesใช้descriptionเดียว ไม่พบ canonical/OG title; titleเปลี่ยนฝั่ง client | วาง page metadata/schema เฉพาะข้อมูลจริงในขั้นH กำหนด canonicalเมื่อมี URLเผยแพร่จริง |

### ภาพหลักฐานของปัญหา

- [ผลลัพธ์ผิดจาก “มากกว่า ฿70k”](focused/catalog-over70k-wrong-result.png)
- [การ์ดก่อน Hover](focused/catalog-image-before-hover.png) / [หลัง Hover](focused/catalog-image-hover.png)
- [ราคา/transform/runtime data/fixed layers](focused/findings.json)
- [Catalog layout shifts — สองตัวอย่างยืนยัน source เป็น Footer](performance/catalog-layout-shifts.json)
- [Contrast calculation](contrast-calculation.json)

## Audit รายหน้าและภาพ Before

ภาพชุดหลักใช้ Chromium ที่1440×1000,768×1024,390×844 และวัดเพิ่มที่1024×768/320×740 รวม50 route×viewport checks กับ3 empty states รวม53 views,36ภาพ ก่อนเปลี่ยนโค้ด การเก็บภาพปิด motion เพื่ออ่าน layout จึงไม่ใช้ภาพเหล่านี้เป็นหลักฐาน performance

| หน้า | สิ่งที่ต้องปรับในขั้น redesign | Desktop / Tablet / Mobile |
|---|---|---|
| Homepage | อัตราส่วน Hero/ตัวอักษร, featured density,จังหวะ section,การ์ดและ entry point Quiz/Compare | [D](before/home-desktop.png) · [T](before/home-tablet.png) · [M](before/home-mobile.png) |
| Catalog | สเกลหัวข้อ/toolbar,อ่าน controls,card rhythm,filter/empty state และแก้70k | [D](before/catalog-desktop.png) · [T](before/catalog-tablet.png) · [M](before/catalog-mobile.png) |
| Guitar Detail | Gallery/summary hierarchy,price/source grouping,spacingและข้อมูลรอง โดยรักษา4ภาพ/สี | [D](before/detail-desktop.png) · [T](before/detail-tablet.png) · [M](before/detail-mobile.png) |
| Brands | ขนาดหัวข้อ/card mark/count,filter toolbar และ spacingแบบเดียวกับCatalog | [D](before/brands-desktop.png) · [T](before/brands-tablet.png) · [M](before/brands-mobile.png) |
| Yamaha Brand Detail | editorial headerและcard variantเดียวกับCatalog;20รุ่นยังครบ | [D](before/brand-detail-desktop.png) · [T](before/brand-detail-tablet.png) · [M](before/brand-detail-mobile.png) |
| Compare | readable same-value text,table grouping,action hierarchyและscroll affordance | [D](before/compare-desktop.png) · [T](before/compare-tablet.png) · [M](before/compare-mobile.png) |
| Quiz Welcome | รูปแบบหัวข้อ/CTAและข้อมูลรองให้เข้าชุด | [D](before/quiz-welcome-desktop.png) · [T](before/quiz-welcome-tablet.png) · [M](before/quiz-welcome-mobile.png) |
| Quiz Question | Option/progress/action rhythmและtap target | [D](before/quiz-question-desktop.png) · [T](before/quiz-question-tablet.png) · [M](before/quiz-question-mobile.png) |
| Quiz Results | ลดcard/type hierarchyที่แย่งกัน รักษาเหตุผลและข้อจำกัดข้อมูล | [D](before/quiz-results-desktop.png) · [T](before/quiz-results-tablet.png) · [M](before/quiz-results-mobile.png) |
| Wishlist | product row/price/actionsและempty stateให้เข้าชุด | [D](before/wishlist-desktop.png) · [T](before/wishlist-tablet.png) · [M](before/wishlist-mobile.png) |

Full-page Desktop: [Homepage](before/home-desktop-full.png), [Catalog](before/catalog-desktop-full.png), [Detail](before/detail-desktop-full.png)

Empty states: [Catalog](before/catalog-empty-mobile.png), [Wishlist](before/wishlist-empty-mobile.png), [Compare](before/compare-empty-mobile.png)

Navbar, Footer, Sidebar และ shared overlays ตรวจจาก sourceร่วมกับหน้าข้างต้น รวม[Mobile Filter](focused/mobile-filter-drawer.png)และ[Mobile Menu](focused/mobile-navigation.png) ส่วนที่ยังเป็น Safari-specific risk คือ desktop mega-menuแบบhover/focusที่1024px, focusค้นหาหลังtimeout350ms และ lightbox safe-area; **ยังไม่ยืนยันว่าเสียใน Safari จริง**

## ผลทดสอบ — แยก checks ที่ผ่านจากปัญหาที่พบ

| Check | ผลจริง |
|---|---|
| `npm run build` | ผ่าน;4.17sในเครื่องทดสอบนี้ |
| `npm run catalog:check` | ผ่าน;200รุ่น/10แบรนด์/20ต่อแบรนด์ ไม่มีduplicate |
| `npm run images:check` | ผ่าน;2 licensed photos+4 project illustrations ในระบบเดิม;197รุ่นใช้placeholder |
| Existing Pacifica/shared integration regression | 79 checksผ่าน ครอบคลุมgallery/สี/lightbox/keyboard/touch,Wishlist,Compare,Home/Brands,Quiz results,Back/Forwardและfallback |
| Drawer / Mobile menu | 4casesที่390/768pxเปิด–ปิดด้วยEscapeและคืนfocusผ่าน;[ผล](focused/dialog-checks.json) |
| Baseline responsive views | 53views ไม่พบ page-level horizontal overflow,console/runtime errorsหรือfailed requests |
| Image/ID integrity | 25ไฟล์ข้อมูล/ภาพ/heroตรงbaseline byte-for-byte; runtime200uniqueIDs,10×20;ทุกactiveIDresolve Detail lookupได้ |
| Pacifica | Gallery4ภาพ ราคา34000; factual colorsยังว่าง ชื่อสีเป็นpresentation metadata ไม่มีรุ่นใหม่ |
| Price preset >70k | **พบข้อผิดพลาด** คืนรุ่น34000แทนempty result |
| Hover full image | **พบข้อผิดพลาด** ขอบภาพถูกครอปขณะscale |
| Local CLS | **พบประเด็นต้องแก้** บางDesktop samples≈0.23611;Catalogยืนยันซ้ำ |
| Full accessibility certification / physical Safari/iPad | **ไม่ได้ทดสอบ/ไม่ได้รับรอง** มีmanual/source/contrast reviewและChromium emulationเท่านั้น |

ผล79checksไม่ใช่คำรับรองว่าเว็บไร้ปัญหา ข้อผิดพลาดที่พบใหม่ด้านบนไม่อยู่ใน assertions ของ regressionเดิม

### Performance ตั้งต้น

ใช้ **Production Build** ที่เสิร์ฟด้วย Vite previewบนLinux วัด7หน้าที่1440/390px รวม14ตัวอย่าง แยกจากการจับภาพและfunctional tests ใช้cold browser contextและรอดู2.8sหลังload ไม่ใช่Lighthouseคะแนนหรือfield Core Web Vitals และไม่จำลองเครือข่ายiPadจริง

- Observed LCPในตัวอย่างนี้:532–1608ms ใช้เป็นbaselineเปรียบเทียบในเครื่องเดียวกันเท่านั้น
- Observed CLSสูงสุด:0.23611ที่Catalog/Detail Desktop;เป้าหมายต่อไป≤0.1โดยต้องวัดซ้ำหลังแก้
- Main catalog chunkประมาณ456.9kB UTF-8 /36.9kB estimated gzip;homepageโหลดchunkนี้ด้วย จึงควรดูการแบ่งข้อมูลตามความจำเป็น แต่ไม่ตัดsource evidenceออกเพื่อลดขนาด
- Font inventory7ไฟล์รวม328,360bytes ไม่ได้แปลว่าโหลดทั้ง7ไฟล์ในทุกหน้า;มีlocal fontsและfont-display:swapอยู่แล้ว
- ไม่พบภาพแตก/overflowใน14production samples แต่ยังไม่มีthrottled network,INP measurement,field dataหรือSafariจริง

รายละเอียด: [Production baseline](performance/baseline.json), [Static bundle/font metrics](performance/static-metrics.json), [measurement script](performance/measure.py)

## Files Added / Modified

รอบนี้เพิ่มเฉพาะ `docs/signature-redesign/`:

- รายงาน Audit,priority/test/integrity records และ logของBuild/Catalog/Images
- `capture-before.py`, `focused-probes.py`, `regression-gallery.py`, `performance/measure.py` และผลJSON
- ภาพBefore/ภาพหลักฐาน/Styleboard
- `proposals/tokens.css`, `design-system.html`, `DESIGN_SYSTEM.md`

**ไม่มีไฟล์ application,product data,image asset,dependencyหรือcontextถูกเปลี่ยน** ไม่มีbugsที่แก้แล้วในรอบนี้;มีbugที่ยืนยันและจัดลำดับไว้ก่อนเริ่มimplementation

## จุดตรวจถัดไป

ตรวจ [Styleboard](../proposals/design-system-desktop.png) และ [Design System proposal](../proposals/DESIGN_SYSTEM.md) ก่อนนำไปใช้กับtokens/Shared Components ส่วน Homepage RedesignรอจุดตรวจถัดจากShared Components ไม่เริ่มอัตโนมัติ
