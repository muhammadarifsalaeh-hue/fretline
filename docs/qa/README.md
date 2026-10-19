# Browser verification

The final production build passed 35 assertions in Chromium. See results.json
and browser-production.txt for the recorded results. Screenshots are manual
visual QA artifacts, not a pixel-diff test.

To rerun with Python Playwright installed and system Chromium available:

```sh
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
# In another terminal:
python docs/qa/browser-qa.py
```

Optional environment variables: FRETLINE_QA_URL, CHROMIUM_BIN.
The browser script uses a fresh context and synthetic favorites/comparison
selections. The supplied mobile screenshot was recaptured with a clean context
at 390 × 1000 to show the initial page without a comparison tray.
