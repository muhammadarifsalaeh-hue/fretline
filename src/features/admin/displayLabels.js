// Presentation labels only. Never use these translated values in RPCs or data.
const PUBLICATION_LABELS = Object.freeze({ draft: 'แบบร่าง', published: 'เผยแพร่แล้ว', hidden: 'ซ่อน' });
const ACTION_LABELS = Object.freeze({ save_draft: 'บันทึกแบบร่าง', publish: 'เผยแพร่', hide: 'ซ่อนสินค้า', register_image: 'เพิ่มรูปภาพ', delete_unused_image: 'ลบรูปภาพที่ไม่ใช้งาน' });

export const publicationLabel = (value) => Object.hasOwn(PUBLICATION_LABELS, value) ? PUBLICATION_LABELS[value] : value;
export const auditActionLabel = (value) => Object.hasOwn(ACTION_LABELS, value) ? ACTION_LABELS[value] : value;
