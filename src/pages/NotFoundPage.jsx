import { useEffect } from 'react';
import { t } from '@/i18n';
import Button from '@/components/ui/Button';

export default function NotFoundPage() {
  useEffect(() => {
    document.title = t('targeted.notFound.docTitle');
  }, []);
  return (
    <section className="container-x flex min-h-[70svh] flex-col items-start justify-center pt-28">
      <p className="font-mono text-sm text-gold">404</p>
      <h1 className="mt-3 font-serif text-5xl leading-none tracking-tight md:text-7xl">{t('targeted.notFound.title')}</h1>
      <p className="mt-5 max-w-md text-mute">{t('targeted.notFound.description')}</p>
      <div className="mt-8 flex gap-3">
        <Button href="/guitars">{t('targeted.notFound.catalog')}</Button>
        <Button href="/" variant="ghost">{t('targeted.notFound.home')}</Button>
      </div>
    </section>
  );
}
