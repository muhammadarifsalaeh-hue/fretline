/**
 * ระบบภาษา: ไทยเป็นภาษาหลัก, อังกฤษเป็นภาษาสำรอง (ใช้ในการทดสอบและเป็นค่าตั้งต้นเมื่อไม่มีคำแปลไทย)
 *  - เปลี่ยนภาษา: localStorage 'fretline:lang' = 'th' | 'en' (ภาษาคงที่ต่อการโหลดหน้า)
 *  - t('key', { n: 3 }) แทนค่า {n} ในข้อความ
 *  - ถ้ามีคีย์ 'key_one' และ n === 1 จะใช้รูปเอกพจน์ (ภาษาอังกฤษ: 1 model / 2 models)
 */
import { en } from './en';
import { th } from './th';

const DICT = { th, en };

function detect() {
  try {
    const saved = localStorage.getItem('fretline:lang');
    if (saved === 'en' || saved === 'th') return saved;
  } catch {
    /* ไม่มี storage: ใช้ค่าเริ่มต้น */
  }
  return 'th';
}

export const LANG = detect();
if (typeof document !== 'undefined') document.documentElement.lang = LANG;

export function t(key, vars) {
  const dict = DICT[LANG];
  let text = dict[key] ?? DICT.en[key] ?? key;
  if (vars && vars.n === 1) text = dict[`${key}_one`] ?? DICT.en[`${key}_one`] ?? text;
  return vars ? text.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? '')) : text;
}
