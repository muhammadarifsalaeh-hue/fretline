// A visual reveal is deliberately separate from a physical pose transition.
// Bones are never interpolated here: an unaudited path between two valid end
// poses can still pass through the wood or another finger. The engine applies
// the next exact pose while hidden, then reveals only an allowed inspection or
// independently reviewed lesson pose. Closing inspection always hides at once.
export function createHandReveal(root, {
  invalidate,
  onProgress = () => {},
  duration = 160,
  requestFrame = globalThis.requestAnimationFrame?.bind(globalThis),
  cancelFrame = globalThis.cancelAnimationFrame?.bind(globalThis),
  now = () => globalThis.performance?.now() ?? Date.now(),
  reducedMotion = () => globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true,
} = {}) {
  const originals = new Map();
  let frame = null, startedAt = 0, disposed = false;

  const rememberMaterials = () => {
    root.traverse((object) => {
      const materials = object.material ? (Array.isArray(object.material) ? object.material : [object.material]) : [];
      materials.forEach((material) => {
        if (!originals.has(material)) originals.set(material, { opacity: material.opacity, transparent: material.transparent });
      });
    });
  };
  const opacity = (amount) => {
    originals.forEach((original, material) => {
      const transparent = original.transparent || amount < 1;
      if (material.transparent !== transparent) { material.transparent = transparent; material.needsUpdate = true; }
      material.opacity = original.opacity * amount;
    });
  };
  const stop = () => {
    if (frame !== null) cancelFrame?.(frame);
    frame = null; opacity(1);
    onProgress({ phase: 'idle', progress: 1 });
  };
  const tick = () => {
    frame = null;
    if (disposed) return;
    // Respect a user enabling reduced motion while this short reveal is in
    // progress too; finish on the next queued frame without another loop.
    const progress = reducedMotion() ? 1 : Math.min(1, Math.max(0, (now() - startedAt) / duration));
    // Ease out without running a permanent render loop or changing pose data.
    opacity(1 - (1 - progress) ** 3);
    onProgress({ phase: progress < 1 ? 'revealing' : 'idle', progress });
    invalidate?.();
    if (progress < 1) frame = requestFrame(tick);
  };
  return {
    start() {
      if (disposed) return;
      stop(); rememberMaterials();
      if (reducedMotion() || !requestFrame || duration <= 0) { opacity(1); invalidate?.(); return; }
      startedAt = now(); opacity(0);
      onProgress({ phase: 'revealing', progress: 0 }); invalidate?.();
      frame = requestFrame(tick);
    },
    // Caller hides before cancelling, so a restored opaque material cannot
    // expose an old chord after its diagram/markers have changed.
    cancel() { if (!disposed) stop(); },
    // A retry disposes the old GLB. Do not retain its materials in this cache.
    reset() { if (!disposed) { stop(); originals.clear(); } },
    dispose() {
      if (disposed) return;
      disposed = true; stop(); originals.clear();
    },
  };
}
