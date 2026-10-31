import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { ChordAudioPlayer, PLAYBACK_RATES } from '../audio/chordAudio';
export function useChordAudio(chord) {
  const player = useRef(null), [rate, setRate] = useState(1), [state, setState] = useState({ status: 'idle' });
  useLayoutEffect(() => { player.current?.stop(); }, [chord.id, rate]);
  useEffect(() => () => { player.current?.dispose(); player.current = null; }, []);
  const toggle = useCallback(() => {
    if (!player.current) player.current = new ChordAudioPlayer({ onState: setState });
    if (player.current.playing) player.current.stop();
    else player.current.play(chord, rate).catch(() => {});
  }, [chord, rate]);
  const changeRate = useCallback((direction) => {
    player.current?.stop();
    setRate(value => PLAYBACK_RATES[Math.max(0, Math.min(PLAYBACK_RATES.length - 1, PLAYBACK_RATES.indexOf(value) + direction))]);
  }, []);
  return { toggle, rate, changeRate, playing: state.status === 'playing', error: state.status === 'error', state,
    canSlowDown: rate > PLAYBACK_RATES[0], canSpeedUp: rate < PLAYBACK_RATES.at(-1) };
}
