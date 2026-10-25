# ผลตรวจท่ามือทั้ง 42 คอร์ด — Batch 2

**ผ่านเชิงเรขาคณิต 3/42 · รับรองเป็นท่าสำหรับสอน 0/42**

ผ่านเชิงเรขาคณิตหมายถึงตรวจเมชมือรวมเสื้อกับตัวเองและกีตาร์จริง ตรวจตัวอย่างผิวภายในไม้ สายเปิด และผิวปลายนิ้วของนิ้วที่ระบุตรงบริเวณเฟรต ไม่ใช่การรับรองความเป็นธรรมชาติหรือ iPad Safari

| คอร์ด | รูปจับสาย 6→1 | คู่ผิวมือ/เสื้อชนกัน | ผลเรขาคณิต | สถานะท่าสอน |
|---|---|---:|---|---|
| C | `x32010` | 0 | ผ่าน | needs-review |
| D | `xx0232` | 370 | ไม่ผ่าน | needs-review |
| E | `022100` | 722 | ไม่ผ่าน | needs-review |
| F | `133211` | 516 | ไม่ผ่าน | needs-review |
| G | `320003` | 352 | ไม่ผ่าน | needs-review |
| A | `x02220` | 472 | ไม่ผ่าน | needs-review |
| B | `x24442` | 284 | ไม่ผ่าน | needs-review |
| Cm | `x35543` | 458 | ไม่ผ่าน | needs-review |
| Dm | `xx0231` | 363 | ไม่ผ่าน | needs-review |
| Em | `022000` | 530 | ไม่ผ่าน | needs-review |
| Fm | `133111` | 416 | ไม่ผ่าน | needs-review |
| Gm | `355333` | 502 | ไม่ผ่าน | needs-review |
| Am | `x02210` | 741 | ไม่ผ่าน | needs-review |
| Bm | `x24432` | 395 | ไม่ผ่าน | needs-review |
| C7 | `x32310` | 308 | ไม่ผ่าน | needs-review |
| D7 | `xx0212` | 600 | ไม่ผ่าน | needs-review |
| E7 | `020100` | 564 | ไม่ผ่าน | needs-review |
| F7 | `131211` | 322 | ไม่ผ่าน | needs-review |
| G7 | `320001` | 327 | ไม่ผ่าน | needs-review |
| A7 | `x02020` | 451 | ไม่ผ่าน | needs-review |
| B7 | `x21202` | 273 | ไม่ผ่าน | needs-review |
| Cmaj7 | `x32000` | 0 | ผ่าน | needs-review |
| Dmaj7 | `xx0222` | 522 | ไม่ผ่าน | needs-review |
| Emaj7 | `021100` | 755 | ไม่ผ่าน | needs-review |
| Fmaj7 | `xx3210` | 363 | ไม่ผ่าน | needs-review |
| Gmaj7 | `320002` | 358 | ไม่ผ่าน | needs-review |
| Amaj7 | `x02120` | 597 | ไม่ผ่าน | needs-review |
| Bmaj7 | `x24342` | 428 | ไม่ผ่าน | needs-review |
| Cm7 | `x35343` | 321 | ไม่ผ่าน | needs-review |
| Dm7 | `xx0211` | 598 | ไม่ผ่าน | needs-review |
| Em7 | `020000` | 484 | ไม่ผ่าน | needs-review |
| Fm7 | `131111` | 509 | ไม่ผ่าน | needs-review |
| Gm7 | `353333` | 625 | ไม่ผ่าน | needs-review |
| Am7 | `x02010` | 0 | ผ่าน | needs-review |
| Bm7 | `x24232` | 351 | ไม่ผ่าน | needs-review |
| Csus2 | `x35533` | 482 | ไม่ผ่าน | needs-review |
| Dsus2 | `xx0230` | 478 | ไม่ผ่าน | needs-review |
| Asus2 | `x02200` | 531 | ไม่ผ่าน | needs-review |
| Csus4 | `x33011` | 443 | ไม่ผ่าน | needs-review |
| Dsus4 | `xx0233` | 328 | ไม่ผ่าน | needs-review |
| Esus4 | `022200` | 457 | ไม่ผ่าน | needs-review |
| Asus4 | `x02230` | 561 | ไม่ผ่าน | needs-review |

39 ท่าที่ไม่ผ่าน Self Collision ถูกปฏิเสธในขั้นแรก จึงไม่อ้างว่าตำแหน่งสัมผัสหรือการชนกีตาร์ผ่าน ส่วน C, Cmaj7 และ Am7 ผ่านชุดตรวจเชิงเรขาคณิตครบทุกขั้น แต่ยังไม่ถูกเปลี่ยนเป็น verified

[ข้อมูลวัดเต็มและ Hash Binding](geometry/summary.json) · Raw Triangle Reports แบบ gzip อยู่ในโฟลเดอร์เดียวกัน

ใช้ข้อมูลคอร์ดเดิมทั้ง 42 แบบโดยไม่เปลี่ยน Frets, Fingers, Barre หรือ Open/Muted Strings เพื่อบังคับให้ผ่าน
