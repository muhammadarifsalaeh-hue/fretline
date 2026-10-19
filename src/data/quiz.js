/**
 * ข้อมูลทั้งหมดของ Quiz "Find My Guitar" — แก้คำถาม/ตัวเลือก/โปรไฟล์กีตาร์ที่ไฟล์นี้ไฟล์เดียว
 * (เพิ่มคำถามใหม่ได้โดยเพิ่ม step แล้วเพิ่มกติกาใน utils/quizScoring.js)
 */
export const QUIZ_STEPS = [
  {
    id: 'type',
    title: 'What would you like to play?',
    hint: 'Pick the family of instrument you have in mind.',
    options: [
      { value: 'electric', label: 'Electric guitar', desc: 'Plugged-in tones, from clean to heavy.' },
      { value: 'acoustic', label: 'Acoustic guitar', desc: 'Natural, resonant sound with no amp needed.' },
      { value: 'classical', label: 'Classical guitar', desc: 'Warm nylon strings and a wide, easy neck.' },
      { value: 'bass', label: 'Bass guitar', desc: 'The low end that holds a band together.' },
      { value: 'any', label: 'Not sure yet', desc: 'Show me the best fit across every type.' },
    ],
  },
  {
    id: 'level',
    title: 'How long have you been playing?',
    hint: 'Be honest. The right guitar depends on where you are today.',
    options: [
      { value: 'beginner', label: 'Just starting', desc: 'New to guitar or playing for under a year.' },
      { value: 'intermediate', label: 'Getting comfortable', desc: 'You know the basics and play regularly.' },
      { value: 'advanced', label: 'Experienced', desc: 'You play often and know what you like.' },
    ],
  },
  {
    id: 'style',
    title: 'What music do you play most?',
    hint: 'Choose the style you will spend the most time on.',
    options: [
      { value: 'rock', label: 'Rock & metal', desc: 'Heavy riffs, big leads and plenty of gain.' },
      { value: 'blues', label: 'Blues & jazz', desc: 'Expressive, warm and dynamic playing.' },
      { value: 'pop', label: 'Pop & indie', desc: 'Bright rhythm parts and modern textures.' },
      { value: 'folk', label: 'Folk & country', desc: 'Strumming, fingerpicking and singing along.' },
      { value: 'classical', label: 'Classical & fingerstyle', desc: 'Nylon-string repertoire and solo arrangements.' },
    ],
  },
  {
    id: 'budget',
    title: 'What is your budget?',
    hint: 'We will favour guitars in this range and flag the ones above it.',
    options: [
      { value: 'low', label: 'Under ฿10,000', desc: 'Solid, honest starter instruments.' },
      { value: 'mid', label: '฿10,000 – ฿30,000', desc: 'The sweet spot for quality and value.' },
      { value: 'high', label: '฿30,000 – ฿70,000', desc: 'Serious instruments with better materials.' },
      { value: 'premium', label: 'Over ฿70,000', desc: 'Top-tier craftsmanship and tone.' },
      { value: 'flex', label: 'Flexible', desc: 'The right guitar matters more than the price.' },
    ],
  },
  {
    id: 'priority',
    title: 'What matters most to you?',
    hint: 'This decides the tie-breaker between similar guitars.',
    options: [
      { value: 'light', label: 'Light and comfortable', desc: 'Easy to hold and play for hours.' },
      { value: 'versatile', label: 'Versatile sound', desc: 'One guitar for many styles and tones.' },
      { value: 'premium', label: 'Premium craftsmanship', desc: 'Materials and build you will keep for years.' },
      { value: 'value', label: 'Best value', desc: 'The most guitar for the money.' },
    ],
  },
];

/** ช่วงราคาของแต่ละตัวเลือก budget (max ไม่จำกัด = Infinity) */
export const BUDGETS = {
  low: { min: 0, max: 10000 },
  mid: { min: 10000, max: 30000 },
  high: { min: 30000, max: 70000 },
  premium: { min: 70000, max: Infinity },
  flex: null,
};

/**
 * โปรไฟล์ของกีตาร์แต่ละรุ่น (key = id ใน guitars.js) ใช้ให้คะแนน
 *   levels   : ระดับผู้เล่นที่เหมาะ
 *   styles   : แนวเพลงที่เหมาะ  (rock | blues | pop | folk | classical)
 *   versatile / premium / value : จุดเด่นเรื่องความหลากหลาย / งานคราฟต์ / ความคุ้มค่า
 * (ข้อมูลเป็นการประเมินเพื่อการสาธิต)
 */
export const GUITAR_PROFILES = {
  'fender-american-professional-ii-stratocaster': { levels: ['intermediate', 'advanced'], styles: ['rock', 'blues', 'pop'], versatile: true, premium: true },
  'gibson-les-paul-standard-60s': { levels: ['intermediate', 'advanced'], styles: ['rock', 'blues'], premium: true },
  'ibanez-rg550-genesis': { levels: ['intermediate', 'advanced'], styles: ['rock'] },
  'yamaha-pacifica-612viifm': { levels: ['beginner', 'intermediate'], styles: ['rock', 'pop', 'blues'], versatile: true, value: true },
  'prs-se-custom-24': { levels: ['intermediate', 'advanced'], styles: ['rock', 'pop', 'blues'], versatile: true },
  'epiphone-casino': { levels: ['intermediate'], styles: ['blues', 'pop', 'rock'] },
  'taylor-214ce': { levels: ['intermediate', 'advanced'], styles: ['folk', 'pop'], versatile: true, premium: true },
  'martin-d-18': { levels: ['intermediate', 'advanced'], styles: ['folk'], premium: true },
  'yamaha-fg800': { levels: ['beginner', 'intermediate'], styles: ['folk', 'pop'], value: true },
  'cordoba-c5': { levels: ['beginner', 'intermediate'], styles: ['classical'], value: true },
  'fender-player-ii-jazz-bass': { levels: ['intermediate', 'advanced'], styles: ['rock', 'blues', 'pop'], versatile: true },
  'ibanez-sr300e': { levels: ['beginner', 'intermediate'], styles: ['rock', 'pop'], value: true },
  'squier-classic-vibe-60s-stratocaster': { levels: ['beginner', 'intermediate'], styles: ['rock', 'pop', 'blues'], value: true },
  'gretsch-g2420-streamliner': { levels: ['intermediate', 'advanced'], styles: ['blues', 'pop', 'rock'] },
  'epiphone-les-paul-standard-50s': { levels: ['beginner', 'intermediate'], styles: ['rock', 'blues'], value: true },
  'taylor-gs-mini': { levels: ['beginner', 'intermediate'], styles: ['folk', 'pop'], value: true },
  'yamaha-c40': { levels: ['beginner'], styles: ['classical'], value: true },
  'fender-player-precision-bass': { levels: ['beginner', 'intermediate', 'advanced'], styles: ['rock', 'blues', 'pop'] },
};
