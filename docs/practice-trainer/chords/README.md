# Practice chord database

The central source is `src/features/practice/data/chords.js`: 42 learner voicings, exactly seven in each of six groups. The original IDs `C`, `G`, `D`, `Em`, `Am` retain their original frets and fingerings. Chords are now ordered by group, with natural roots C, D, E, F, G, A, B; the suspended group contains the seven explicitly requested choices.

| Group | IDs |
| --- | --- |
| Major | C, D, E, F, G, A, B |
| Minor | Cm, Dm, Em, Fm, Gm, Am, Bm |
| Dominant seventh | C7, D7, E7, F7, G7, A7, B7 |
| Major seventh | Cmaj7, Dmaj7, Emaj7, Fmaj7, Gmaj7, Amaj7, Bmaj7 |
| Minor seventh | Cm7, Dm7, Em7, Fm7, Gm7, Am7, Bm7 |
| Suspended | Csus2, Dsus2, Asus2, Csus4, Dsus4, Esus4, Asus4 |

## Reading the data

All six-entry arrays run **low E → high e**, physical strings **6 → 1** in E2 A2 D3 G3 B3 E4 tuning. A fret of `null` means do not play the string; `0` means open. Fingers are `null` for open/muted strings and 1=index, 2=middle, 3=ring, 4=little. Notes include octave and chord-appropriate sharps or flats.

Barres use inclusive physical string numbers: `{ finger: 1, fret: 3, fromString: 5, toString: 1 }` means index finger across A through high e at fret 3. Another finger can fret a covered string higher. An open, muted, or lower-fretted sounding string cannot be crossed by the declared barre. `baseFret` is 1 for an open shape, otherwise its lowest fretted position. `openStrings` and `mutedStrings` also use physical string numbers.

Each object includes bilingual instruction arrays and explicit diagram/hand status reasons. Every nested object/array is frozen. `PRACTICE_CHORD_BY_ID` and `BY_ID` are the same lookup; `CHORD_TYPES` provides `{ id, label: { th, en } }`.

## Voicing decisions

- C7 uses the familiar open `x32310`, fingers `[null,3,2,4,1,null]`. Its sounding notes are C3 E3 Bb3 C4 E4. Omitting fifth G is conventional and keeps the beginner shape. It is explicitly recorded as `omittedTones: ['G']`; root, third and seventh are all required. This is the sole omission permitted by the validator.
- Csus2 uses `x35533`: index barre at fret 3 from string 5 to 1, ring on D5, little finger on G5. Notes C3 G3 C4 D4 G4 contain C–D–G, with no third. Its open alternative `x30033` is valid but is not the selected voicing.
- Csus4 uses `x33011`: ring A3, little D3, G open, index mini-barre B/e1. It contains C–F–G and no third.
- Bmaj7 uses complete `x24342`, rather than an open form omitting F#. F, Fm, Gm, Bm and their seventh derivatives use conventional movable shapes.
- Barre chords require practice; “learner voicing” does not mean every shape is an introductory open chord.

## Validation and status

`npm run practice:check` passes **56 checks, zero failures**. It verifies the exact 42 IDs, seven per type, retained original choices, standard tuning, absolute note pitches, quality intervals, the single documented C7 omission, fret limits, finger/barre coherence, five-fret span, bilingual text, immutable nested data, and geometry. Ten deliberately corrupted records establish that meaningful mistakes are rejected. The reusable `validatePracticeChord()` returns `{ valid, errors }`; `noteToMidi()` handles sharp/flat note spellings with octave.

An additional independently authored audit reports **86/86 passing checks** at `../tests/reports/chord-audit.json`. This checks different fixtures and tuning calculations. It does not certify the rendered SVG or any anatomical pose.

All 42 `diagramStatus.status` values are **verified** after independent musical checks and actual full/compact SVG review in both Chromium and Linux WebKit on 2026-10-25. All 42 `handPose.status` values remain **unavailable** in the central musical data: no fabricated human pose is attached to these records. The runtime pose engine validates the model hash, actual named rig and each chord’s collision/contact/anatomy/multi-view evidence separately. An unapproved hand remains hidden in lessons. Source reads, pitch correctness and finger-array consistency alone cannot prove anatomical correctness.

See [sources.md](sources.md) for the pages actually fetched and read, [status.json](status.json) for the machine-readable snapshot, and [practice-check.txt](practice-check.txt) for the check transcript.
