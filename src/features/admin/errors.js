export function adminError(error) {
  if(error?.code==='40001'||error?.message?.includes('CONFLICT'))return 'ข้อมูลถูกแก้ไขจากอีกหน้าจอแล้ว กรุณาเปิดรุ่นนี้ใหม่ก่อนบันทึก';
  if(error?.message?.includes('Invalid login'))return 'อีเมลหรือรหัสผ่านไม่ถูกต้อง';
  if(error?.code==='PGRST202'||error?.message?.includes('schema cache'))return 'ยังไม่ได้รัน SQL ตั้งค่า Supabase กรุณาดูขั้นตอนตั้งค่า';
  if(error?.message?.includes('Admin access'))return 'บัญชีนี้ไม่มีสิทธิ์แอดมิน';
  return 'ดำเนินการไม่สำเร็จ กรุณาตรวจการเชื่อมต่อแล้วลองอีกครั้ง';
}
