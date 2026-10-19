/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0A0A0A',
        surface: '#141414',
        'surface-2': '#1C1C1C',
        line: '#2A2A2A',
        bone: '#F5F5F2',
        mute: '#8A8A85',
        paper: '#F4F2EE',
        gold: { DEFAULT: '#C8A15A', soft: '#E0C58C' },
      },
      fontFamily: {
        // Anuphan = ฟอนต์หลักของภาษาไทย (และตัวอักษรละตินในข้อความทั่วไป)
        // Instrument Serif = โลโก้/ชื่อรุ่นภาษาอังกฤษ — ตัวอักษรไทยจะตกไปใช้ Anuphan อัตโนมัติ
        serif: ['"Instrument Serif"', 'Anuphan', 'serif'],
        sans: ['Anuphan', 'Geist', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'Anuphan', 'ui-monospace', 'monospace'],
      },
      transitionTimingFunction: {
        premium: 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
      keyframes: {
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(24px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        heroGuitar: {
          from: { opacity: '0', transform: 'translateX(64px) scale(1.04)' },
          to: { opacity: '1', transform: 'translateX(0) scale(1)' },
        },
        marquee: {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        },
        pingSoft: {
          '0%': { transform: 'scale(0.6)', opacity: '0.8' },
          '100%': { transform: 'scale(2.4)', opacity: '0' },
        },
        scrollLine: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        toastIn: {
          from: { opacity: '0', transform: 'translateY(12px) scale(0.96)' },
          to: { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
      },
      animation: {
        'fade-up': 'fadeUp 900ms cubic-bezier(0.22,1,0.36,1) both',
        'fade-in': 'fadeIn 400ms ease both',
        'hero-guitar': 'heroGuitar 1600ms cubic-bezier(0.22,1,0.36,1) both',
        marquee: 'marquee 40s linear infinite',
        'ping-soft': 'pingSoft 2.4s cubic-bezier(0,0,0.2,1) infinite',
        'scroll-line': 'scrollLine 2.2s cubic-bezier(0.65,0,0.35,1) infinite',
        'toast-in': 'toastIn 400ms cubic-bezier(0.22,1,0.36,1) both',
      },
    },
  },
  plugins: [],
};
