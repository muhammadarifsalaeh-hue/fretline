import { useEffect } from 'react';
import Button from '@/components/ui/Button';

export default function NotFoundPage() {
  useEffect(() => {
    document.title = 'Page not found — Fretline';
  }, []);
  return (
    <section className="container-x flex min-h-[70svh] flex-col items-start justify-center pt-28">
      <p className="font-mono text-sm text-gold">404</p>
      <h1 className="mt-3 font-serif text-5xl leading-none tracking-tight md:text-7xl">This page is out of tune.</h1>
      <p className="mt-5 max-w-md text-mute">The page you’re looking for doesn’t exist or has moved.</p>
      <div className="mt-8 flex gap-3">
        <Button href="/guitars">Browse guitars</Button>
        <Button href="/" variant="ghost">Back home</Button>
      </div>
    </section>
  );
}
