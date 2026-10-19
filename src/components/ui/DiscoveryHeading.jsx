import { t } from '@/i18n';
import AppLink from './AppLink';

/** Compact editorial heading shared by the Phase 5 discovery pages. */
export default function DiscoveryHeading({ eyebrow, title, description, breadcrumbs = [], children, aside, serif = false }) {
  return (
    <header className="container-x phase5-heading">
      <nav aria-label="Breadcrumb" className="discovery-breadcrumb">
        <AppLink href="/">{t('nav.home')}</AppLink>
        {breadcrumbs.map(({ label, href }, index) => (
          <span key={`${label}-${index}`} className="inline-flex items-center gap-2">
            <span aria-hidden="true">›</span>
            {href ? <AppLink href={href}>{label}</AppLink> : <span aria-current="page">{label}</span>}
          </span>
        ))}
      </nav>
      <p className="discovery-kicker" lang="en">{eyebrow}</p>
      <div className="phase5-title-row">
        <div>
          <h1 className={serif ? 'font-serif phase5-brand-name' : ''}>{title}</h1>
          {description && <p className="phase5-intro">{description}</p>}
          {children}
        </div>
        {aside}
      </div>
    </header>
  );
}
