# Phase 4 verification

- Production Chromium browser suite: 86/86 checks.
- Development/Strict Mode edge suite: 7/7 checks.
- Scoring, provenance, comparison analysis and selection logic: 19/19 checks.
- Total: 112 checks passed. Browser JSON records exact console/request results.

```sh
npm run build
npm run catalog:check
npm run images:check
npm run phase4:check
npm run preview -- --host 127.0.0.1 --port 4173 --strictPort
# Another terminal, with Python Playwright and system Chromium available:
python docs/qa-phase4/browser-qa.py
# Edge checks use the development server (including React Strict Mode):
npm run dev -- --host 127.0.0.1 --port 5177 --strictPort
# Another terminal:
python docs/qa-phase4/edge-qa.py
```

QA environment variables: FRETLINE_QA_URL, FRETLINE_DEV_URL, CHROMIUM_BIN.
Playwright/Chromium are environment tooling; no application dependencies added.
Clipboard success/denial are controlled API stubs. The empty catalog exists only
inside one isolated browser context and resets on reload. Test fixtures never
change production guitar records. No Safari/iPad hardware or WebKit run claimed.

Screenshots use a real browser at desktop 1440px, tablet 768px and mobile 390px.
Compare includes four known catalog models; missing photos remain illustrations.
Question screenshots show the selected-answer state. Result scores are heuristic
alignment scores; they are not ratings. Finite animations are fast-forwarded for
stable captures. The layout was visually reviewed against the original reference
in the conversation, without a numerical pixel-diff claim.
