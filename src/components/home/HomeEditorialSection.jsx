import Button from '@/components/ui/Button';
import { ArrowRightIcon } from '@/components/ui/Icons';
import '@/styles/home-editorial.css';

/** A photographic gateway to an existing tool, with one clear action. */
export default function HomeEditorialSection({ id, eyebrow, title, accent, description, photo, href, action }) {
  return <section id={id} className={`home-editorial home-editorial--${id}`} aria-labelledby={`home-${id}-title`}>
    <div className="home-editorial-photo" aria-hidden="true">
      <img src={photo.src} srcSet={photo.srcSet} sizes="100vw" width={photo.width} height={photo.height}
        alt="" loading="lazy" decoding="async" />
    </div>
    <div className="container-x home-editorial-inner">
      <div className="home-editorial-copy">
        <p className="signature-section-eyebrow">{eyebrow}</p>
        <h2 id={`home-${id}-title`}>{title}<br /><span>{accent}</span></h2>
        <p className="home-editorial-description">{description}</p>
        <Button href={href} size="lg" className="home-editorial-cta">{action}<ArrowRightIcon size={19} /></Button>
      </div>
    </div>
  </section>;
}
