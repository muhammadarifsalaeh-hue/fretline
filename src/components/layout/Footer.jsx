import { FOOTER_COLUMNS } from '@/data/navigation';
import { t } from '@/i18n';
import AppLink from '@/components/ui/AppLink';
import Logo from './Logo';

/** Footer: ทุกลิงก์พาไปหน้าที่มีอยู่จริง (ไม่มีลิงก์/ฟอร์มที่กดแล้วไม่ทำงาน) */
export default function Footer() {
  return (
    <footer className="overflow-hidden border-t border-line bg-[#050505]">
      <div className="container-x pt-14 md:pt-20">
        <div className="grid gap-10 border-b border-line pb-12 md:grid-cols-12 md:gap-10 md:pb-16">
          <div className="md:col-span-6">
            <Logo />
            <p className="mt-5 max-w-sm text-sm leading-relaxed text-mute">{t('footer.tagline')}</p>
            <p className="mt-4 max-w-sm text-xs leading-relaxed text-mute/80">{t('footer.dataNote')}</p>
          </div>
          <div className="grid grid-cols-2 gap-8 md:col-span-6 md:gap-10">
            {FOOTER_COLUMNS.map((col) => (
              <nav key={col.title} aria-label={col.title}>
                <p className="text-sm font-medium text-bone">{col.title}</p>
                <ul className="mt-5 space-y-3">
                  {col.links.map((link) => (
                    <li key={link.href}>
                      <AppLink href={link.href} className="text-sm text-mute transition-colors hover:text-gold">
                        {link.label}
                      </AppLink>
                    </li>
                  ))}
                </ul>
              </nav>
            ))}
          </div>
        </div>

        <p className="py-6 text-xs text-mute">{t('footer.copyright', { year: new Date().getFullYear() })}</p>
      </div>

      {/* ตัวอักษรขนาดมหึมาเป็นลายเซ็นท้ายเว็บ */}
      <div aria-hidden="true" className="select-none text-center font-serif text-[27vw] leading-[0.78] tracking-tighter text-[#141414] md:text-[22vw]">
        Fretline
      </div>
    </footer>
  );
}
