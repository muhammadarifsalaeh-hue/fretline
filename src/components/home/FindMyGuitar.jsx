import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import GuitarArt from '@/components/ui/GuitarArt';
import { ArrowRightIcon } from '@/components/ui/Icons';
import Reveal from '@/components/ui/Reveal';

/** An entry into the existing URL-driven quiz, using its real first question. */
export default function FindMyGuitar() {
  const firstQuestion = QUIZ_STEPS[0];
  const instrumentOptions = firstQuestion.options.filter((option) => option.value !== 'any');

  return (
    <section id="find" className="home-find-section" aria-labelledby="home-find-title">
      <div className="container-x home-find-layout">
        <Reveal className="home-experience-copy">
          <p className="home-experience-eyebrow"><span aria-hidden="true" />03 / FIND YOUR GUITAR</p>
          <h2 id="home-find-title">
            {t('signature.find.titleLead')}<br />{t('signature.find.titleEnd')}
          </h2>
          <p className="home-experience-description">{t('signature.find.body', { n: QUIZ_STEPS.length })}</p>
          <Button href="/find-my-guitar" size="lg" className="home-experience-cta">
            {t('signature.find.cta')}<ArrowRightIcon size={18} />
          </Button>
        </Reveal>

        <Reveal className="home-find-panel">
          <div className="home-find-caption">
            <span>FIND MY GUITAR</span>
            <span aria-hidden="true">01 / {String(QUIZ_STEPS.length).padStart(2, '0')}</span>
          </div>
          <div className="home-find-track" aria-hidden="true">
            {QUIZ_STEPS.map((step) => <span key={step.id} />)}
          </div>
          <h3>{firstQuestion.title}</h3>
          <div className="home-find-choices">
            {instrumentOptions.map((option) => (
              <AppLink
                key={option.value}
                href={`/find-my-guitar?${new URLSearchParams({ type: option.value, step: '1' })}`}
                className="home-find-choice"
                data-home-quiz-option={option.value}
                aria-label={t('signature.find.optionAria', { type: option.label })}
              >
                <GuitarArt type={option.value} className="home-find-instrument" aria-hidden="true" />
                <span>{option.label}</span>
                <ArrowRightIcon size={15} className="home-find-choice-arrow" />
              </AppLink>
            ))}
          </div>
          <div className="home-find-bottom">
            <p>{t('signature.find.preview')}</p>
            <AppLink href="/find-my-guitar" className="home-experience-icon-link" aria-label={t('signature.find.cta')}>
              <ArrowRightIcon size={19} />
            </AppLink>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
