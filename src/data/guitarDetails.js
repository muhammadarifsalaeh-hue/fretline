/**
 * ข้อมูลรายละเอียดของกีตาร์แต่ละรุ่น (key = id ใน guitars.js)
 *   description : คำอธิบายรุ่น (ประโยคแรกใช้เป็นสรุปสั้นบนหัวหน้า)
 *   bridge / controls : สเปกเพิ่มเติม
 *   colors : สีที่มีขาย  { name, hex }  (hex ใส่ gradient ได้ เช่น 'linear-gradient(...)')
 *   gallery : (ไม่บังคับ) รูปหลายมุมของรุ่นนี้ [{ src, label }] ใช้แทนรูปจาก src/assets/guitars/<id>/
 *             โดยปกติไม่ต้องใส่ — วางไฟล์รูปในโฟลเดอร์ของรุ่นนั้นแทน (ดู data/guitarImages.js)
 * (ข้อมูลเป็นตัวอย่างสำหรับสาธิต)
 */
const SUNBURST = 'linear-gradient(135deg,#e0b050 0%,#a8501e 55%,#1d1208 100%)';
const CHERRY_BURST = 'linear-gradient(135deg,#c2452a 0%,#7a1d12 60%,#2a0a06 100%)';

export const DETAILS = {
  'fender-american-professional-ii-stratocaster': {
    description:
      'A modern refinement of the double-cutaway that defined electric guitar. The American Professional II adds a contoured neck heel, a rolled fingerboard edge and V-Mod II single-coils for a clear, articulate voice. It stays comfortable through long sessions and responds to every change in touch.',
    bridge: '2-point synchronized tremolo, bent steel saddles',
    controls: 'Master volume, 2 tone, 5-way switch',
    colors: [
      { name: 'Olympic White', hex: '#EDEAE0' },
      { name: '3-Color Sunburst', hex: SUNBURST },
      { name: 'Miami Blue', hex: '#3A8FD0' },
      { name: 'Mystic Black', hex: '#141414' },
    ],
  },
  'gibson-les-paul-standard-60s': {
    description:
      'The solid-body classic with a slim 60s neck profile and a carved maple top. Burstbucker humbuckers deliver a thick, singing sustain that sits comfortably from warm clean to saturated lead. A heavyweight in both feel and presence.',
    bridge: 'ABR-1 tune-o-matic, aluminum stop bar tailpiece',
    controls: '2 volume, 2 tone, 3-way toggle',
    colors: [
      { name: 'Iced Tea', hex: '#9A5B2E' },
      { name: 'Heritage Cherry Sunburst', hex: CHERRY_BURST },
      { name: 'Ebony', hex: '#111111' },
    ],
  },
  'ibanez-rg550-genesis': {
    description:
      'A fast, thin-neck shred machine reissued from a 1987 original. Twenty-four frets, a locking tremolo and a versatile HSH layout make it equally at home with hard rock, metal and fusion. Light enough to play for hours.',
    bridge: 'Edge double-locking tremolo',
    controls: 'Volume, tone, 5-way switch',
    colors: [
      { name: 'Road Flare Red', hex: '#C0281C' },
      { name: 'Desert Sun Yellow', hex: '#E4C13A' },
      { name: 'Purple Neon', hex: '#8A3FFC' },
    ],
  },
  'yamaha-pacifica-612viifm': {
    description:
      'A well-built all-rounder that punches well above its price. The flamed maple top, HSS pickup layout and coil-split option cover everything from jangly cleans to heavy drive. A dependable first serious guitar and a great upgrade from a starter.',
    bridge: 'Vintage-style tremolo',
    controls: 'Master volume, tone, 5-way switch with coil split',
    colors: [
      { name: 'Black', hex: '#111111' },
      { name: 'Yellow Natural Satin', hex: '#D9B45A' },
      { name: 'Sunset Blue', hex: '#2C4A8A' },
    ],
  },
  'prs-se-custom-24': {
    description:
      'Elegant lines, a carved maple top and 24 frets on a 25-inch scale. Two humbuckers with coil-tap options give both thick lead tones and bright rhythm sounds. Polished playability straight out of the case.',
    bridge: 'PRS patented tremolo',
    controls: 'Volume, tone, 3-way toggle, coil tap',
    colors: [
      { name: 'Charcoal Burst', hex: '#3A3A3D' },
      { name: 'Vintage Cherry', hex: '#7A1D1D' },
      { name: 'Turquoise', hex: '#2AA3A0' },
    ],
  },
  'epiphone-casino': {
    description:
      'A thin hollowbody with a warm, open voice and the bite of P-90 pickups. Loved for blues, indie and vintage rock and roll. Lightweight and resonant with plenty of character.',
    bridge: 'Tune-o-matic, trapeze tailpiece',
    controls: '2 volume, 2 tone, 3-way toggle',
    colors: [
      { name: 'Vintage Sunburst', hex: SUNBURST },
      { name: 'Natural', hex: '#D9B27A' },
      { name: 'Cherry', hex: '#7A1D1D' },
    ],
  },
  'taylor-214ce': {
    description:
      'A Grand Auditorium that balances clarity and warmth, with a solid spruce top and built-in ES2 electronics. The cutaway opens up the upper frets for lead playing. Ready for the living room and the stage.',
    bridge: 'Ebony bridge, compensated saddle',
    controls: 'ES2 volume and tone (upper bout)',
    colors: [
      { name: 'Natural', hex: '#D8B27A' },
      { name: 'Sunburst', hex: SUNBURST },
    ],
  },
  'martin-d-18': {
    description:
      'The dreadnought that shaped bluegrass, folk and country. A solid spruce top over solid mahogany gives a dry, punchy tone with a strong fundamental. A long-term instrument that tends to sound better with age.',
    bridge: 'Ebony bridge, compensated bone saddle',
    controls: 'None (acoustic)',
    colors: [{ name: 'Natural', hex: '#C9A06A' }],
  },
  'yamaha-fg800': {
    description:
      'A solid spruce top dreadnought that sets the standard for affordable acoustics. Full, balanced tone and reliable build quality make it a favourite for beginners and gigging players alike. Great value for money.',
    bridge: 'Rosewood bridge',
    controls: 'None (acoustic)',
    colors: [
      { name: 'Natural', hex: '#D6AC72' },
      { name: 'Sunburst', hex: SUNBURST },
      { name: 'Black', hex: '#111111' },
    ],
  },
  'cordoba-c5': {
    description:
      'A warm, rounded nylon-string with a solid cedar top. The comfortable neck and balanced response suit students and experienced players. A good entry point to classical and flamenco-inspired styles.',
    bridge: 'Rosewood tie-block bridge',
    controls: 'None (acoustic)',
    colors: [{ name: 'Natural Cedar', hex: '#C2763A' }],
  },
  'fender-player-ii-jazz-bass': {
    description:
      'A slim, fast neck and two single-coil pickups for the classic growl and clarity of the Jazz Bass. Blend them for a full scooped tone or solo one for punch. A versatile pick for any genre.',
    bridge: 'Standard 4-saddle bass bridge',
    controls: 'Volume, volume, tone',
    colors: [
      { name: 'Black', hex: '#111111' },
      { name: 'Sienna Sunburst', hex: SUNBURST },
      { name: 'Olympic White', hex: '#EDEAE0' },
    ],
  },
  'ibanez-sr300e': {
    description:
      'A lightweight, slim-profile bass with active electronics for fast playing and plenty of tonal options. The 3-band EQ lets you shape the sound without leaving your seat. Excellent for modern rock and funk.',
    bridge: 'Accu-cast B120 bridge',
    controls: 'Volume, balance, 3-band EQ',
    colors: [
      { name: 'Iron Pewter', hex: '#5E5E63' },
      { name: 'Black', hex: '#111111' },
    ],
  },
  'squier-classic-vibe-60s-stratocaster': {
    description:
      'Vintage looks and feel at an approachable price. Alnico single-coils and a 60s-style neck bring a bright, chiming tone. A very popular first electric that stays useful as you improve.',
    bridge: 'Vintage-style synchronized tremolo',
    controls: 'Master volume, 2 tone, 5-way switch',
    colors: [
      { name: 'Olympic White', hex: '#EDEAE0' },
      { name: 'Lake Placid Blue', hex: '#7FB2D6' },
      { name: '3-Color Sunburst', hex: SUNBURST },
    ],
  },
  'gretsch-g2420-streamliner': {
    description:
      'A hollowbody with Broad’Tron humbuckers and a strong, clear attack. It has the character of classic Gretsch with modern reliability. Great for rockabilly, indie and jangly rock.',
    bridge: 'Adjusto-Matic bridge, stop bar tailpiece',
    controls: 'Volume per pickup, master tone, 3-way toggle',
    colors: [
      { name: 'Walnut Stain', hex: '#6B4426' },
      { name: 'Havana Burst', hex: SUNBURST },
      { name: 'Black', hex: '#111111' },
    ],
  },
  'epiphone-les-paul-standard-50s': {
    description:
      'A faithful take on the 50s Les Paul with a chunky neck profile and ProBucker humbuckers. Strong sustain and a full, warm voice at a friendly price. A solid choice for rock, blues and classic hard rock.',
    bridge: 'LockTone tune-o-matic, stop bar tailpiece',
    controls: '2 volume, 2 tone, 3-way toggle',
    colors: [
      { name: 'Heritage Cherry Sunburst', hex: CHERRY_BURST },
      { name: 'Ebony', hex: '#111111' },
      { name: 'Tobacco Burst', hex: SUNBURST },
    ],
  },
  'taylor-gs-mini': {
    description:
      'A compact body with a surprisingly big voice. Easy to carry and comfortable to play, it is a favourite for travel, songwriting and small players. Solid top construction gives it real depth.',
    bridge: 'Ebony bridge',
    controls: 'None (acoustic)',
    colors: [{ name: 'Natural Mahogany', hex: '#A65A2E' }],
  },
  'yamaha-c40': {
    description:
      'A friendly, affordable classical guitar made for learning. Smooth nylon-string response and a comfortable neck make the first months easier. Dependable build that stays in tune.',
    bridge: 'Rosewood bridge',
    controls: 'None (acoustic)',
    colors: [{ name: 'Natural', hex: '#D2A468' }],
  },
  'fender-player-precision-bass': {
    description:
      'The bass that defined the sound of rock and soul. A split-coil Precision pickup delivers a solid, punchy low end that sits perfectly in a mix. Simple controls and rock-solid reliability.',
    bridge: 'Standard 4-saddle bass bridge',
    controls: 'Volume, tone',
    colors: [
      { name: 'Black', hex: '#111111' },
      { name: 'Sienna Sunburst', hex: SUNBURST },
      { name: 'Olympic White', hex: '#EDEAE0' },
    ],
  },
};

/** คะแนนรีวิว (ข้อมูลตัวอย่าง) — ไม่มีรุ่นไหนใน map = ไม่แสดงคะแนน */
export const RATINGS = {
  'fender-american-professional-ii-stratocaster': { score: 4.8, count: 214 },
  'gibson-les-paul-standard-60s': { score: 4.7, count: 168 },
  'ibanez-rg550-genesis': { score: 4.6, count: 92 },
  'yamaha-pacifica-612viifm': { score: 4.6, count: 341 },
  'prs-se-custom-24': { score: 4.7, count: 127 },
  'epiphone-casino': { score: 4.5, count: 76 },
  'taylor-214ce': { score: 4.8, count: 189 },
  'martin-d-18': { score: 4.9, count: 143 },
  'yamaha-fg800': { score: 4.6, count: 402 },
  'cordoba-c5': { score: 4.5, count: 118 },
  'fender-player-ii-jazz-bass': { score: 4.7, count: 156 },
  'ibanez-sr300e': { score: 4.5, count: 64 },
  'squier-classic-vibe-60s-stratocaster': { score: 4.7, count: 233 },
  'gretsch-g2420-streamliner': { score: 4.6, count: 88 },
  'epiphone-les-paul-standard-50s': { score: 4.6, count: 271 },
  'taylor-gs-mini': { score: 4.7, count: 205 },
  'yamaha-c40': { score: 4.4, count: 310 },
  'fender-player-precision-bass': { score: 4.8, count: 177 },
};
