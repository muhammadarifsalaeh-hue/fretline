import { t } from '@/i18n';

const nf = new Intl.NumberFormat('en-US');
export const NOT_SPECIFIED = t('common.notSpecified');
/** ราคาไม่ทราบ (price = null) แสดงเป็น "สอบถามราคา" ไม่เดา/ไม่แปลงสกุลเงินเอง */
export const formatPrice = (n) => (n == null ? t('price.onRequest') : `฿${nf.format(n)}`);
export const formatKg = (v) => (v == null ? NOT_SPECIFIED : `${v} ${t('unit.kg')}`);
export const formatInch = (v) => (v == null ? NOT_SPECIFIED : `${v}"`);
