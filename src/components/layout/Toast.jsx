import { useShop } from '@/context/ShopContext';

/** ข้อความแจ้งเตือนสั้น ๆ (เพิ่ม/ลบ Wishlist หรือ Compare) */
export default function Toast() {
  const { toast } = useShop();
  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-[calc(150px+env(safe-area-inset-bottom))] z-[70] flex justify-center px-4 lg:bottom-28"
    >
      {toast && (
        <div key={toast.id} className="animate-toast-in rounded-full bg-bone px-5 py-3 text-sm font-medium text-ink shadow-2xl">
          {toast.message}
        </div>
      )}
    </div>
  );
}
