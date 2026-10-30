export const PRODUCT_IMAGE_SIZE = 1200;
export const PRODUCT_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export function validateImageFile(file) {
  if (!PRODUCT_IMAGE_TYPES.includes(file.type)) throw new Error('รองรับ JPG, PNG และ WebP เท่านั้น');
  if (!(file.size > 0) || file.size > 25 * 1024 * 1024) throw new Error('ภาพต้องมีขนาดมากกว่า 0 และไม่เกิน 25 MB');
}

/** Compute a square canvas without stretching, cropping or upscaling pixels. */
export function imagePlan(width, height, mode = 'square') {
  if (!['square', 'pad'].includes(mode)) throw new Error('รูปแบบจัดภาพไม่ถูกต้อง');
  if (![width, height].every((n) => Number.isInteger(n) && n > 0)) throw new Error('อ่านขนาดภาพไม่สำเร็จ');
  if (width !== height && mode !== 'pad') throw new Error('ภาพไม่เป็นสัดส่วน 1:1 กรุณาเลือกจัดลงกรอบดำหรือเลือกภาพใหม่');
  const side = Math.min(PRODUCT_IMAGE_SIZE, Math.max(width, height));
  const scale = Math.min(1, side / width, side / height);
  const drawWidth = Math.round(width * scale), drawHeight = Math.round(height * scale);
  return { width: side, height: side, drawWidth, drawHeight, x: (side - drawWidth) / 2, y: (side - drawHeight) / 2,
    originalWidth: width, originalHeight: height, padded: width !== height, downscaled: scale < 1 };
}

async function readImage(file, callback) {
  validateImageFile(file);
  const url = URL.createObjectURL(file);
  try {
    const image = new Image(); image.src = url;
    try { await image.decode(); } catch { throw new Error('อ่านไฟล์ภาพไม่สำเร็จ กรุณาเลือกไฟล์ใหม่'); }
    if (!image.naturalWidth || !image.naturalHeight) throw new Error('อ่านขนาดภาพไม่สำเร็จ');
    return await callback(image);
  } finally { URL.revokeObjectURL(url); }
}

export function inspectImage(file) {
  return readImage(file, (image) => ({ width: image.naturalWidth, height: image.naturalHeight,
    square: image.naturalWidth === image.naturalHeight,
    standard: image.naturalWidth === PRODUCT_IMAGE_SIZE && image.naturalHeight === PRODUCT_IMAGE_SIZE,
    small: Math.max(image.naturalWidth, image.naturalHeight) < PRODUCT_IMAGE_SIZE }));
}

export function compressImage(file, { mode = 'square' } = {}) {
  return readImage(file, async (image) => {
    const plan = imagePlan(image.naturalWidth, image.naturalHeight, mode);
    const canvas = document.createElement('canvas'); canvas.width = plan.width; canvas.height = plan.height;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('เตรียมภาพไม่สำเร็จ');
    ctx.fillStyle = '#000000'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(image, plan.x, plan.y, plan.drawWidth, plan.drawHeight);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/webp', .9));
    canvas.width = 0; canvas.height = 0;
    if (!blob || !['image/webp', 'image/png'].includes(blob.type) || blob.size > 8 * 1024 * 1024) throw new Error('ย่อภาพไม่สำเร็จ กรุณาเลือกภาพที่เล็กลง');
    return { ...plan, blob, extension: blob.type === 'image/webp' ? 'webp' : 'png' };
  });
}
