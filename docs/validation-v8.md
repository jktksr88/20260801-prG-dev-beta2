# GROE v8 Validation Report

Release: `8.0.0`

## Automated validation

- `41 passed` in the complete Python test suite.
- JavaScript syntax validation passed for `backend/app/static/assets/app.v8.js`.
- Static browser smoke test passed.
- Fresh Alembic migration completed.
- Initial seed inserted exactly 50 crop profiles; a second seed inserted zero.
- `/`, `/api/v1/build`, `/api/v1/health`, `/api/v1/ready`, `/assets/app.v8.js` and `/assets/styles.v8.css` returned HTTP 200 in a local clean boot.

## Visual browser validation

The production HTML, CSS and JavaScript were executed in headless Chromium with controlled API responses. The following screens were rendered and captured:

1. Landing page with visible guest-beta and new-feature indicators.
2. Location autocomplete dropdown.
3. Selected location with temperature, humidity, rain, wind and update time.
4. Plan detail with standardized crop codes, infrastructure legend and pot inventory.
5. Plant cards below the map and expanded guide modal.
6. Guest diary without sign-in.

Screenshots are stored in `docs/screenshots/`.

## Client-feedback coverage

- Location dropdown has an internal Indonesian-city fallback and remote Open-Meteo search.
- Weather first uses the server route and can retry Open-Meteo directly from the browser before showing the climate fallback.
- Each crop slug maps to one stable colour and two-letter symbol across map, legend, card and guide.
- Legend includes soil, pot, hanging pot, access path, rack/stand, trellis and compost.
- Recommended pot diameter, depth and litres are returned and included in spatial footprints.
- Plant cards are a dedicated section below the map.
- The 50-crop catalogue is absent from public navigation and remains internal metadata.
- Sign-in is removed from the beta interface.
- Plans and diary entries persist locally in the browser.
- Guest diary calls the AI-capable backend endpoint and retains deterministic fallback when no API key is configured.

## Live-service limitation

The build environment could not resolve the public Render hostname. The live deployment remains objectively identifiable through `/api/v1/build`, the `X-GROE-Build` header, versioned assets and the visible footer label.
