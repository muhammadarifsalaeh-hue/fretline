# WebKit timing correction

The initial production acceptance run passed 29/32 scenarios. All three remaining failures were the brand rail's automatic speed on Linux WebKit 26.5, with only 2–8 pixels observed in a nominal 800ms window. Chromium's rail passed. The initial failure evidence is preserved separately.

## Actual cause

The hook clamped every animation frame's elapsed time to 48ms. WebKit's first software-rendered frames of this photographic page had actual gaps of 196, 339, 510 and sometimes over 1,000ms. Clamping those gaps discarded animation time and made the rail run slowly. The original trace stayed in `auto` throughout; this was not a user-scroll event being misclassified as manual interaction.

The hook now advances using its actual `requestAnimationFrame` timestamp and initializes the clock when starting. Existing offscreen/document-hidden lifecycle handling resets that clock, so a hidden tab does not accumulate a catch-up jump. The configured speed remains **30 CSS pixels per second**; manual gesture handling, resume delay/ramp, keyboard focus, reduced motion and the seamless measured-width loop are unchanged.

## Measurement evidence

An arbitrary read between frames can observe the previous frame's position while attaching a newer `performance.now()` timestamp. A later frame then catches up, making that short sample look too fast. This was demonstrated after the code fix by the `unaligned-samples.json` readings. It is not evidence that the configured velocity should be lowered.

`requested-positions.json` captures actual `scrollLeft` setter calls and RAF timestamps. For example, the target changes from 1840 at 879ms to 1924.3 at 3690ms: 84.3 pixels / 2.811 seconds = **30.0px/s**.

For a bound speed measurement, sample both the visible position and animation timestamp inside the same RAF callback, before and after the observation interval. The actual WebKit results in `aligned-samples.json` were:

| Viewport | Actual animation interval | Distance | Measured rate |
|---|---:|---:|---:|
| Desktop | 971ms | 29px | 29.866px/s |
| Tablet | 822ms | 25px | 30.414px/s |
| Mobile | 831ms | 25px | 30.084px/s |

The 30px/s target and the loop-boundary frame-displacement requirement are not weakened. These development-source timing probes complement the final production acceptance suite; they do not replace it.

## Native wheel/touch momentum

After the speed correction, production acceptance exposed a separate real interaction bug: a native horizontal wheel event could move only 20–41 pixels and then remain still in manual mode, rather than completing the requested 180-pixel movement. The settled traces distinguished that cancellation from later automatic movement.

`onScroll` adopted the browser's new scroll position through `writePosition`, which assigned that unchanged value back to `scrollLeft`. WebKit treats this assignment as a programmatic scroll and cancels its ongoing native wheel/touch momentum. `writePosition` now updates its internal position and only assigns the native property when the actual requested position differs. Automatic movement and seamless period rebasing still write as required; adopting an unchanged native value does not.

The actual development-source WebKit carousel scenarios subsequently passed **3/3** at Desktop, Tablet and Mobile, retaining the strict 27–33px/s speed check, native manual wheel movement greater than 70 pixels, automatic resume, the existing loop frame-displacement ceiling and the no-blank-frame requirement. Actual results and source hashes are in [carousel-after-momentum-fix.json](carousel-after-momentum-fix.json). This is a focused development check; the root agent performs the final production rebuild and complete regression suite.

## Rendering limitation

Initial low frame rate in Linux WebKit software rendering remains visible in the trace. Promoting the rail to a composited layer and temporarily removing its mask were tested independently and did not improve those initial stalls, so no unsupported CSS optimization was shipped. The normal viewport's later steady-state loop and gesture behavior must still be checked by production acceptance. This report does not claim a physical iPad running Safari was tested.
