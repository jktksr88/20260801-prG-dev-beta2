# GROE Client Feedback Release v7.0.0

This release is a full replacement for the currently deployed Python-only Render package. It addresses all six client-feedback items in one build and adds a visible build marker so deployment can be verified without guessing.

## 1. Location and current weather

- Location is entered through type-ahead autocomplete after three characters.
- Results appear in a dropdown and retain name, administrative area, latitude, longitude and elevation.
- Open-Meteo is the primary geocoding and current-weather provider.
- A curated Indonesian-city fallback keeps the dropdown usable if the external geocoding service is temporarily unavailable.
- The weather panel shows current temperature, relative humidity, current rainfall/precipitation, wind speed, apparent temperature, condition label and update time.
- Users can refresh weather or optionally use browser geolocation.
- Loading, live-provider, no-results and reduced-confidence fallback states are explicit.

## 2. Consistent 2D map visualization and legend

- Each crop slug maps deterministically to one crop symbol and one colour.
- The same visual is reused on the map, crop key, recommendation card and detailed guide.
- The map has infrastructure keys for direct soil, pot, hanging pot, access path, rack/stand, trellis and compost.
- A separate crop key identifies every crop used in the selected plan.

## 3. Pot recommendation and capacity

- Container crops receive recommended diameter, depth and volume.
- Recommendations remain traceable to the stored minimum dimensions, mature width, preferred spacing and preferred root depth.
- Layout capacity uses the larger of preferred plant spacing and recommended pot diameter.
- Pot footprint therefore affects quantity and placement rather than appearing only as explanatory text.
- A grouped pot inventory is displayed below the map.

## 4. Plant recommendation cards

- The scaled 2D layout remains the result-page visual hero.
- Recommendation cards appear in a dedicated section below the map.
- Cards show the consistent crop visual, suitability, harvest timing, sunlight, ideal pot or spacing, quantity and pot note.
- The complete guide opens in a separate modal with planting, care, harvest, warnings and pot information.

## 5. Internal 50-crop metadata

- The public crop-catalogue navigation and page are removed from the deployed browser application.
- The 50 crop profiles remain available to the planner, spatial engine, recommendation cards and diary through structured backend metadata.
- Render ignores the archived React development folder, preventing an older catalogue screen from being built accidentally.

## 6. Guest diary and optional AI

- A user may open and test GROE Diary without an account.
- Guest entries are stored in that browser through local storage.
- The guest endpoint receives the selected plan, selected crop, growth stage, planner conditions, weather context and recent guest entries.
- When an OpenAI key is configured, the backend can provide cautious AI-supported advice.
- Without a key or when the provider fails, the entry is retained and deterministic guidance is returned.
- Sign-in is retained only for saved gardens and cross-device/server-persisted diary history.

## Deployment verification

Every response includes:

```text
X-GROE-Build: 7.0.0
```

The following endpoint must return build `7.0.0` after deployment:

```text
/api/v1/build
```

The production page loads uniquely versioned assets:

```text
/assets/app.v7.js
/assets/styles.v7.css
```

The footer also displays `Beta build 7.0.0`. These checks distinguish a real v7 deployment from an older cached or incorrectly uploaded build.
