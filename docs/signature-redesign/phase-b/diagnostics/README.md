# Earlier test-harness observations

These reports are preserved for transparency. They predate readiness fixes to the test harness and are not the final site acceptance. `acceptance-functional.json` caught a measurement before the lazy Catalog heading was ready; `acceptance-before-menu-wait.json` caught a keyboard action before the reopened menu ceased being inert. The partial style rerun in `acceptance.json` passed its ten selected cases. The final complete result is `../acceptance-final.json` (18/18). Failure screenshots in `../failures/` belong to these earlier attempts, including the interrupted/BrokenPipe run.

No product errors or failed requests were ignored. The harness now waits for rendered headings, debounced picker results, interactive menu visibility and loaded images. Intentionally hidden ancestor layers are excluded when deciding which images must be visible; visible artwork remains subject to completion/decode/opacity checks.
