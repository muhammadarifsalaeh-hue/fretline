import { BUDGETS, GUITAR_PROFILES, QUIZ_STEPS } from '@/data/quiz';
import { GUITARS } from '@/data/guitars';
import { formatPrice } from './format';

/**
 * ระบบให้คะแนน:
 *   ประเภท 30 | ระดับผู้เล่น 20 | แนวเพลง 20 | งบประมาณ 20 | สิ่งที่สำคัญที่สุด 10 | คะแนนรีวิว สูงสุด 5
 * แล้วปรับเป็นเปอร์เซ็นต์ (สูงสุด 99%) — คะแนนรีวิวช่วยตัดสินเมื่อคะแนนเท่ากัน
 * ถ้าประเภทไม่ตรง คะแนนรวมจะถูกลดลงมาก เพื่อไม่ให้กีตาร์คนละประเภทขึ้นอันดับต้น
 */
const MAX_SCORE = 105;
const LEVELS = ['beginner', 'intermediate', 'advanced'];
const TYPE_LABEL = { electric: 'Electric', acoustic: 'Acoustic', classical: 'Classical', bass: 'Bass' };

export const labelOf = (stepId, value) =>
  QUIZ_STEPS.find((s) => s.id === stepId)?.options.find((o) => o.value === value)?.label ?? value;

/** อ่านคำตอบจาก URL — คืน null ถ้ายังตอบไม่ครบหรือค่าไม่ถูกต้อง */
export function readAnswers(params) {
  const answers = {};
  for (const step of QUIZ_STEPS) {
    const value = params.get(step.id);
    if (!step.options.some((o) => o.value === value)) return null;
    answers[step.id] = value;
  }
  return answers;
}

export function scoreGuitar(guitar, answers) {
  const profile = GUITAR_PROFILES[guitar.id] ?? guitar.profile ?? { levels: [], styles: [] };
  const reasons = [];
  const caveats = [];
  let score = 0;

  // ประเภท (30)
  const typeMatch = answers.type === 'any' || guitar.category === answers.type;
  if (typeMatch) {
    score += 30;
    if (answers.type !== 'any') reasons.push(`${TYPE_LABEL[guitar.category]} guitar, as you asked`);
  }

  // ระดับผู้เล่น (20)
  const wanted = LEVELS.indexOf(answers.level);
  if (profile.levels.includes(answers.level)) {
    score += 20;
    reasons.push(`Well suited to ${labelOf('level', answers.level).toLowerCase()} players`);
  } else if (profile.levels.some((l) => Math.abs(LEVELS.indexOf(l) - wanted) === 1)) {
    score += 8;
  }

  // แนวเพลง (20)
  if (profile.styles.includes(answers.style)) {
    score += 20;
    reasons.push(`Great for ${labelOf('style', answers.style).toLowerCase()}`);
  }

  // งบประมาณ (20)
  const budget = BUDGETS[answers.budget];
  if (!budget) {
    score += 14;
  } else if (guitar.price == null) {
    caveats.push('Price on request, so your budget could not be checked');
    score += 6;
  } else if (guitar.price >= budget.min && guitar.price <= budget.max) {
    score += 20;
    reasons.push(`Within your budget (${labelOf('budget', answers.budget)})`);
  } else if (guitar.price > budget.max) {
    caveats.push(`${formatPrice(guitar.price)} is above your budget`);
    if (guitar.price <= budget.max * 1.2) score += 10;
  } else {
    if (guitar.price >= budget.min * 0.8) score += 10;
    caveats.push('Priced below your range, so you may have room to step up');
  }

  // สิ่งที่สำคัญที่สุด (10)
  const w = guitar.specs.weightKg;
  if (answers.priority === 'light') {
    if (w == null) {
      // น้ำหนักไม่ทราบ: ไม่ให้คะแนนส่วนนี้
    } else if (w <= 3.5) {
      score += 10;
      reasons.push(`Lightweight at ${w} kg`);
    } else if (w <= 3.9) score += 5;
  } else if (answers.priority === 'versatile' && profile.versatile) {
    score += 10;
    reasons.push('Versatile pickups for many tones');
  } else if (answers.priority === 'premium' && (profile.premium || (guitar.price != null && guitar.price >= 60000))) {
    score += 10;
    reasons.push('Premium build and materials');
  } else if (answers.priority === 'value' && profile.value) {
    score += 10;
    reasons.push('Strong value for the price');
  }

  // คะแนนรีวิว (สูงสุด 5): ช่วยแยกอันดับเมื่อคะแนนอื่นเท่ากัน
  if (guitar.rating) score += Math.max(0, (guitar.rating.score - 4) * 5);

  if (!typeMatch) score *= 0.35;
  return { guitar, score: Math.min(99, Math.round((score / MAX_SCORE) * 100)), reasons, caveats };
}

/**
 * จัดอันดับกีตาร์ตามคำตอบ แสดงเฉพาะรุ่นที่เหมาะจริง (คะแนน ≥ minScore)
 * ยกเว้นอันดับ 1 ที่แสดงเสมอ
 */
export function rankGuitars(answers, limit = 3, minScore = 40) {
  return GUITARS.map((g) => scoreGuitar(g, answers))
    .sort((a, b) => b.score - a.score || (b.guitar.rating?.score ?? 0) - (a.guitar.rating?.score ?? 0))
    .filter((m, i) => i === 0 || m.score >= minScore)
    .slice(0, limit);
}

/** ลิงก์ไป Catalog พร้อม filter ที่สอดคล้องกับคำตอบ (ประเภท + งบ) */
export function catalogUrlFor(answers) {
  const p = new URLSearchParams();
  if (answers.type !== 'any') p.set('type', answers.type);
  const b = BUDGETS[answers.budget];
  if (b) {
    if (b.min > 0) p.set('min', String(b.min));
    if (Number.isFinite(b.max)) p.set('max', String(b.max));
  }
  const qs = p.toString();
  return qs ? `/guitars?${qs}` : '/guitars';
}
