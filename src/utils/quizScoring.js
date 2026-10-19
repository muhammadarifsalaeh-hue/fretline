import { BUDGETS, GUITAR_PROFILES, QUIZ_STEPS } from '@/data/quiz';
import { GUITARS } from '@/data/guitars';
import { t } from '@/i18n';
import { formatPrice } from './format';
import { trustedPrice, trustedWeight, verifiedRating } from './dataTrust';

// Preserve the original weights, 105-point scale, 99% cap and type penalty.
export const SCORE_WEIGHTS = Object.freeze({ type: 30, level: 20, style: 20, budget: 20, priority: 10, rating: 5 });
export const MAX_SCORE = Object.values(SCORE_WEIGHTS).reduce((sum, value) => sum + value, 0);
const LEVELS = ['beginner', 'intermediate', 'advanced'];

export const labelOf = (stepId, value) => QUIZ_STEPS.find((step) => step.id === stepId)?.options.find((option) => option.value === value)?.label ?? value;

export function readPartialAnswers(params) {
  return Object.fromEntries(QUIZ_STEPS.flatMap((step) => {
    const value = params.get(step.id);
    return step.options.some((option) => option.value === value) ? [[step.id, value]] : [];
  }));
}

export function readAnswers(params) {
  const answers = readPartialAnswers(params);
  return QUIZ_STEPS.every((step) => answers[step.id]) ? answers : null;
}

export function scoreGuitar(guitar, answers) {
  const profile = GUITAR_PROFILES[guitar.id] ?? guitar.profile ?? { levels: [], styles: [] };
  const levels = profile.levels ?? [];
  const styles = profile.styles ?? [];
  const reasons = [];
  const caveats = [];
  const points = { type: 0, level: 0, style: 0, budget: 0, priority: 0, rating: 0 };
  const typeMatch = answers.type === 'any' || guitar.category === answers.type;
  if (typeMatch) {
    points.type = SCORE_WEIGHTS.type;
    if (answers.type !== 'any') reasons.push(t('score.type', { type: t(`category.${guitar.category}`) }));
  }

  const wanted = LEVELS.indexOf(answers.level);
  if (levels.includes(answers.level)) {
    points.level = SCORE_WEIGHTS.level;
    reasons.push(t('score.level', { level: labelOf('level', answers.level) }));
  } else if (levels.some((level) => Math.abs(LEVELS.indexOf(level) - wanted) === 1)) points.level = 8;
  if (styles.includes(answers.style)) {
    points.style = SCORE_WEIGHTS.style;
    reasons.push(t('score.style', { style: labelOf('style', answers.style) }));
  }
  caveats.push(t(levels.length || styles.length ? 'score.profileEstimate' : 'score.profileMissing'));

  // Unverified sample prices follow the existing unknown-price branch, never the within-budget branch.
  const budget = BUDGETS[answers.budget];
  const price = trustedPrice(guitar);
  if (!budget) points.budget = 14;
  else if (price == null) { points.budget = 6; caveats.push(t('score.budgetUnknown')); }
  else if (price >= budget.min && price <= budget.max) {
    points.budget = SCORE_WEIGHTS.budget;
    reasons.push(t('score.budget', { budget: labelOf('budget', answers.budget) }));
  } else if (price > budget.max) {
    caveats.push(t('score.overBudget', { price: formatPrice(price) }));
    if (price <= budget.max * 1.2) points.budget = 10;
  } else {
    if (price >= budget.min * 0.8) points.budget = 10;
    caveats.push(t('score.belowBudget'));
  }

  const weight = trustedWeight(guitar);
  if (answers.priority === 'light') {
    if (weight != null && weight <= 3.5) { points.priority = SCORE_WEIGHTS.priority; reasons.push(t('score.light', { weight })); }
    else if (weight != null && weight <= 3.9) points.priority = 5;
    else if (weight == null) caveats.push(t('score.weightUnknown'));
  } else if (answers.priority === 'versatile' && profile.versatile) {
    points.priority = SCORE_WEIGHTS.priority; reasons.push(t('score.versatile'));
  } else if (answers.priority === 'premium' && (profile.premium || (price != null && price >= 60000))) {
    points.priority = SCORE_WEIGHTS.priority; reasons.push(t('score.premium'));
  } else if (answers.priority === 'value' && profile.value) {
    points.priority = SCORE_WEIGHTS.priority; reasons.push(t('score.value'));
  }

  const rating = verifiedRating(guitar);
  if (rating) points.rating = Math.min(SCORE_WEIGHTS.rating, Math.max(0, (rating.score - 4) * 5));
  const rawScore = Object.values(points).reduce((sum, value) => sum + value, 0) * (typeMatch ? 1 : 0.35);
  return { guitar, score: Math.min(99, Math.round(rawScore / MAX_SCORE * 100)), rawScore, points, reasons, caveats, typeMatch };
}

/** A minimum applies to every result; never force an unsuitable first recommendation. */
export function rankGuitars(answers, limit = 3, minScore = 40, items = GUITARS) {
  return items.map((guitar) => scoreGuitar(guitar, answers))
    .sort((a, b) => b.score - a.score || (verifiedRating(b.guitar)?.score ?? 0) - (verifiedRating(a.guitar)?.score ?? 0))
    .filter((match) => match.score >= minScore)
    .slice(0, limit);
}

export function catalogUrlFor(answers) {
  const params = new URLSearchParams();
  if (answers.type !== 'any') params.set('type', answers.type);
  const budget = BUDGETS[answers.budget];
  if (budget) {
    if (budget.min > 0) params.set('min', String(budget.min));
    if (Number.isFinite(budget.max)) params.set('max', String(budget.max));
  }
  return params.size ? `/guitars?${params}` : '/guitars';
}
