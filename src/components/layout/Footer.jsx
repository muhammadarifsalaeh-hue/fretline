import { FOOTER_COLUMNS } from '@/data/navigation';
import { t } from '@/i18n';
import AppLink from '@/components/ui/AppLink';
import Logo from './Logo';

/** Footer: ทุกลิงก์พาไปหน้าที่มีอยู่จริง (ไม่มีลิงก์/ฟอร์มที่กดแล้วไม่ทำงาน) */
export default function Footer() {
  return (
    <footer className="site-footer overflow-hidden border-t border-line bg-ink">
      <div className="site-footer-inner container-x pt-14 md:pt-20">
        <div className="grid gap-10 border-b border-line pb-12 md:grid-cols-12 md:gap-10 md:pb-16">
          <div className="site-footer-brand md:col-span-6">
            <Logo />
            <p className="mt-5 max-w-sm text-[15px] leading-7 text-mute">{t('footer.tagline')}</p>
            <p className="site-footer-note mt-4 max-w-sm text-sm leading-7 text-mute">{t('footer.dataNote')}</p>
            <AppLink href="/image-credits" className="site-footer-link mt-3 inline-flex min-h-11 items-center text-sm text-gold underline-offset-4 hover:underline">{t('p6.images.indexLink')}</AppLink>
          </div>
          <div className="site-footer-columns grid grid-cols-2 gap-8 md:col-span-6 md:gap-10">
            {FOOTER_COLUMNS.map((col) => (
              <nav key={col.title} aria-label={col.title}>
                <h2 className="site-footer-heading text-sm font-medium text-bone">{col.title}</h2>
                <ul className="mt-5 space-y-3">
                  {col.links.map((link) => (
                    <li key={link.href}>
                      <AppLink href={link.href} className="site-footer-link inline-flex min-h-11 items-center text-sm text-mute transition-colors hover:text-gold">
                        {link.label}
                      </AppLink>
                    </li>
                  ))}
                </ul>
              </nav>
            ))}
          </div>
        </div>

        <p className="site-footer-copyright py-6 text-[13px] leading-6 text-mute">{t('footer.copyright', { year: new Date().getFullYear() })}</p>
      </div>

      {/* ตัวอักษรขนาดมหึมาเป็นลายเซ็นท้ายเว็บ */}
      <div aria-hidden="true" className="footer-watermark mx-auto max-w-[1100px] select-none px-5 text-surface">
        <svg viewBox="0 0 1000 235" aria-hidden="true" focusable="false" className="w-full overflow-visible">
          <text x="500" y="215" textAnchor="middle" fill="currentColor" fontFamily="Instrument Serif, serif" fontSize="290" textLength="960" lengthAdjust="spacingAndGlyphs">Fretline</text>
        </svg>
      </div>
    </footer>
  );
}
