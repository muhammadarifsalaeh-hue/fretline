// รวม className แบบง่าย ๆ (ข้ามค่า falsy)
export const cn = (...classes) => classes.filter(Boolean).join(' ');
