# Independent batch integration review

Reviewed the saved candidates, exact audit outputs and integration/preservation
helpers. This review did not fit a hand, change runtime data, launch a browser,
or approve anatomy.

- Em7, E7 and Fmaj7 saved candidate root/bone transform hashes bind to their
  passing real-mesh audit records. Those records report zero combined
  skin/sleeve self crossings, zero guitar crossings, zero rejected wood samples,
  correct-owner palmar contacts, and passing open-string clearance.
- `integrate-batch-3.py` checks the actual model and central musical-source
  SHA-256 values, exact candidate transform identity, each mechanical gate and
  the candidate chord ID before setting only geometric collision/contact flags.
  It explicitly keeps `needs-review`, `reviewed: false`, `anatomyPassed: false`
  and `multiViewReviewed: false`. It does not approve a teaching pose.
- The helper preserves every other runtime pose record. The separate preservation
  checker compares all 197 protected site files and four music/model/rig files
  byte-for-byte with `74c2076`; it also compares all non-integrated pose objects.
- The integration helper requires a separate full-library audit after writing the
  final JSON. Per-candidate success must not be reported as all-42 success, and
  any candidate added later must receive a fresh source-to-rendered fingerprint
  check and exact audit.
- Rejected Am, Em, C7, D, Dsus2, G, F and Dm trials remain evidence, not teaching
  poses. Some trials remove all self crossings but still miss contacts or hit
  strings/frets/wood. A zero self-crossing count alone is insufficient.

The finite forearm/sleeve source, extended proximal-finger silhouette and final
anatomical presentation remain separate visual limitations. Neither this review
nor Linux browser tests establish physical iPad Safari performance or a safe
swept physical animation path.
