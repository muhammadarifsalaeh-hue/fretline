/**
 * รูปบรรยากาศ (ไม่ใช่รูปสินค้า) — Hero, หมวดหมู่, แบรนด์, แถบ Quiz
 *
 * ตอนนี้ทุกช่องเป็น null โดยตั้งใจ: ผมตรวจสอบรูปจากอินเทอร์เน็ตไม่ได้ว่าเป็นกีตาร์ประเภท/ยี่ห้อที่ตรงจริง
 * ช่องที่เป็น null จะแสดงภาพเส้นร่าง/ตัวอักษรที่ออกแบบไว้แทน (ดูแล้วไม่ว่างเปล่า)
 * ใส่รูปจริงได้ที่นี่  เช่น  hero: '/images/hero/hero.webp'  (วางไฟล์ใน public/images/...)
 * ต้องเป็นรูปที่ตรงกับความหมายของช่องนั้น เช่น ช่อง bass ต้องเป็นรูปกีตาร์เบส
 */
export const IMAGES = {
  hero: null,
  findMyGuitar: null,

  categories: {
    electric: null,
    acoustic: null,
    classical: null,
    bass: null,
  },

  brands: {
    fender: null,
    yamaha: null,
    taylor: null,
  },
};
