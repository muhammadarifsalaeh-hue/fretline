/** จุดเรืองแสงบนกีตาร์ — hover/focus เพื่อดูสเปก (บนมือถือแตะได้) */
export default function HeroHotspot({ x, y, title, detail }) {
  return (
    <div className="group absolute z-10" style={{ left: `${x}%`, top: `${y}%` }}>
      <button
        type="button"
        aria-label={`${title}: ${detail}`}
        className="relative grid h-11 w-11 -translate-x-1/2 -translate-y-1/2 place-items-center"
      >
        <span aria-hidden="true" className="absolute h-4 w-4 animate-ping-soft rounded-full bg-gold/70" />
        <span aria-hidden="true" className="relative h-3 w-3 rounded-full bg-gold shadow-[0_0_16px_4px_rgba(200,161,90,0.55)]" />
      </button>
      <div
        role="tooltip"
        className="pointer-events-none absolute left-1/2 top-6 w-max max-w-[220px] -translate-x-1/2 translate-y-1 rounded-xl border border-white/10 bg-ink/90 px-4 py-2.5 opacity-0 backdrop-blur-md transition duration-300 ease-premium group-focus-within:translate-y-0 group-focus-within:opacity-100 group-hover:translate-y-0 group-hover:opacity-100"
      >
        <p className="text-xs text-mute">{title}</p>
        <p className="font-mono text-[13px] text-bone">{detail}</p>
      </div>
    </div>
  );
}
