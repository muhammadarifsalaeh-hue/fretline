export async function compressImage(file) {
  if (!['image/jpeg','image/png','image/webp'].includes(file.type)) throw new Error('รองรับ JPG, PNG และ WebP เท่านั้น');
  if (file.size>25*1024*1024) throw new Error('ภาพต้องมีขนาดไม่เกิน 25 MB');
  const url=URL.createObjectURL(file);
  try {
    const image=new Image(); image.src=url;
    await image.decode();
    const scale=Math.min(1,1800/Math.max(image.naturalWidth,image.naturalHeight));
    const canvas=document.createElement('canvas');
    canvas.width=Math.round(image.naturalWidth*scale); canvas.height=Math.round(image.naturalHeight*scale);
    const ctx=canvas.getContext('2d');
    if (!ctx || !canvas.width || !canvas.height) throw new Error('อ่านภาพไม่สำเร็จ');
    ctx.drawImage(image,0,0,canvas.width,canvas.height);
    const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/webp',.85));
    if (!blob || blob.size>8*1024*1024) throw new Error('ย่อภาพไม่สำเร็จ กรุณาเลือกภาพที่เล็กลง');
    return {blob,width:canvas.width,height:canvas.height,extension:blob.type==='image/webp'?'webp':'png'};
  } finally { URL.revokeObjectURL(url); }
}
