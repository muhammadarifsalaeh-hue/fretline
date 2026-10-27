# Actual screenshot review

An independent read-only QA agent inspected more than 34 actual Chromium and WebKit screenshots across Home, Catalog, Quiz, Compare, and Practice, including the final 1024×1366 portrait Home edge. No new blocking readability, text clipping, or horizontal overflow issue was observed.

The restored Home has one large Practice card on the left and the original Find/Compare cards on the right at desktop/landscape. Portrait and mobile, including 1024×1366, stack exactly three cards with readable text and gold actions.

Mobile Practice retains the original left-edge neck crop, confirmed against both baseline engine captures. This does not establish full-neck visibility on small screens. Fixed navigation and the selected-Compare tray can overlap scrolled captures as in the original UI.

These captures use real Linux Chromium and WebKit engines with browser viewport/touch simulation. No physical iPad or native iPadOS Safari test was performed.
