// Educational chord tones from the canonical notes. No recordings or network
// downloads, and no audio context until the learner taps a playback button.
const PITCHES = Object.freeze({ C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 });
export const PLAYBACK_RATES = Object.freeze([0.5, 0.75, 1, 1.25, 1.5]);
export function chordTones(chord) {
  if (!Array.isArray(chord?.notes) || chord.notes.length !== 6) throw new Error('CHORD_NOTES_UNAVAILABLE');
  return chord.notes.flatMap((note, index) => {
    if (note === null) return [];
    const match = /^([A-G])([#b]?)(-?\d+)$/.exec(note);
    if (!match) throw new Error('CHORD_NOTE_INVALID');
    const midi = (Number(match[3]) + 1) * 12 + PITCHES[match[1]] + (match[2] === '#' ? 1 : match[2] === 'b' ? -1 : 0);
    return [{ string: 6 - index, note, midi, frequency: 440 * 2 ** ((midi - 69) / 12) }];
  });
}
export function strumOffsets(count, rate = 1) {
  if (!PLAYBACK_RATES.includes(rate)) throw new RangeError('INVALID_PLAYBACK_RATE');
  return Array.from({ length: count }, (_, index) => index * 0.12 / rate);
}
export class ChordAudioPlayer {
  constructor({ onState = () => {}, contextFactory } = {}) {
    this.onState = onState; this.contextFactory = contextFactory; this.context = null;
    this.voices = new Set(); this.revision = 0; this.disposed = false; this.playing = false;
  }
  async play(chord, rate = 1) {
    if (this.disposed) return;
    const tones = chordTones(chord), offsets = strumOffsets(tones.length, rate);
    if (!tones.length) throw new Error('CHORD_NOTES_UNAVAILABLE');
    this.stop(); const revision = ++this.revision;
    try {
      if (!this.context) {
        const AudioContext = globalThis.AudioContext || globalThis.webkitAudioContext;
        if (!this.contextFactory && !AudioContext) throw new Error('AUDIO_UNAVAILABLE');
        this.context = this.contextFactory ? this.contextFactory() : new AudioContext({ latencyHint: 'interactive' });
        const real = new Float32Array(9), imaginary = new Float32Array([0, 1, .52, .28, .16, .1, .06, .03, .02]);
        this.wave = this.context.createPeriodicWave(real, imaginary);
        this.filter = this.context.createBiquadFilter(); this.filter.type = 'lowpass';
        this.filter.frequency.value = 3400; this.filter.Q.value = .5;
        this.filter.connect(this.context.destination);
      }
      // Called in the original tap stack, before any await, for iPad Safari.
      if (this.context.state !== 'running') await this.context.resume();
      if (this.context.state !== 'running') throw new Error('AUDIO_UNAVAILABLE');
      if (this.disposed || revision !== this.revision) return;
      const base = this.context.currentTime + .025;
      this.playing = true;
      this.onState({ status: 'playing', chordId: chord.id, rate, tones, offsets });
      tones.forEach((tone, index) => {
        const oscillator = this.context.createOscillator(), gain = this.context.createGain();
        const start = base + offsets[index], amplitude = .22 / Math.sqrt(tones.length);
        oscillator.setPeriodicWave(this.wave); oscillator.frequency.value = tone.frequency;
        gain.gain.setValueAtTime(.0001, start);
        gain.gain.exponentialRampToValueAtTime(amplitude, start + .008);
        gain.gain.exponentialRampToValueAtTime(amplitude * .24, start + .23);
        gain.gain.exponentialRampToValueAtTime(.0001, start + 2.35);
        oscillator.connect(gain); gain.connect(this.filter);
        const voice = { oscillator, gain }; this.voices.add(voice);
        oscillator.onended = () => {
          this.voices.delete(voice); oscillator.disconnect(); gain.disconnect();
          if (!this.voices.size && !this.disposed && revision === this.revision) {
            this.playing = false; this.onState({ status: 'idle' });
          }
        };
        oscillator.start(start); oscillator.stop(start + 2.38);
      });
    } catch (error) {
      if (this.disposed || revision !== this.revision) return;
      this.stop(); this.onState({ status: 'error' }); throw error;
    }
  }
  stop() {
    this.revision++; this.playing = false;
    const now = this.context?.currentTime ?? 0;
    for (const { oscillator, gain } of this.voices) {
      try {
        if (gain.gain.cancelAndHoldAtTime) gain.gain.cancelAndHoldAtTime(now);
        else { gain.gain.cancelScheduledValues(now); gain.gain.setValueAtTime(.04, now); }
        gain.gain.exponentialRampToValueAtTime(.0001, now + .015);
        oscillator.stop(now + .025);
      } catch { /* An already-ended voice needs no second stop. */ }
    }
    this.voices.clear();
    if (!this.disposed) this.onState({ status: 'idle' });
  }
  dispose() {
    if (this.disposed) return;
    this.disposed = true; this.stop(); this.onState = () => {};
    this.filter?.disconnect();
    this.context?.close?.().catch(() => {});
  }
}
