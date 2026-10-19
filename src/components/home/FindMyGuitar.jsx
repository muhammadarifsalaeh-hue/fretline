import { t } from '@/i18n';
import { IMAGES } from '@/data/images';
import Button from '@/components/ui/Button';
import Reveal from '@/components/ui/Reveal';
import ArtBackdrop from '@/components/ui/ArtBackdrop';
import SmartImage from '@/components/ui/SmartImage';

/** แถบเชิญชวนทำ Quiz ก่อน Footer */
export default function FindMyGuitar() {
  return (
    <section id="find" className="relative isolate overflow-hidden bg-ink">
      {IMAGES.findMyGuitar ? (
        <SmartImage src={IMAGES.findMyGuitar} alt="" className="absolute inset-0 -z-20" imgClassName="opacity-60" />
      ) : (
        <ArtBackdrop type="electric" anchor="right" className="absolute inset-0 -z-20" />
      )}
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-gradient-to-r from-ink via-ink/80 to-ink/30" />

      <div className="container-x section-y">
        <Reveal className="max-w-xl">
          <h2 className="font-sans text-3xl font-medium leading-[1.15] tracking-tight md:text-5xl">{t('find.title')}</h2>
          <p className="mt-5 max-w-md text-base leading-relaxed text-bone/75 md:text-lg">
            {t('find.body')}
          </p>
          <Button href="/find-my-guitar" size="lg" className="mt-9 w-full sm:w-auto">
            {t('find.button')}
          </Button>
        </Reveal>
      </div>
    </section>
  );
}
