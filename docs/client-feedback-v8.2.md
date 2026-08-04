# GROE v8.2 — Multi-crop diary and truthful vertical map

## Diary recognition

- Free-form English and Indonesian diary notes remain the only required input.
- Added common name and spelling variants, including `pokcoy`, `pok choy`, `bok choy`, `caisin`, `caysim`, `sawi hijau`, and `choy sum`.
- One note can resolve several crops in mention order.
- Straightforward matches use deterministic bilingual metadata first.
- The optional AI provider is used only for uncertain recognition, and returned slugs are verified against crops in the selected plan.
- Multi-crop notes receive separate guidance for each detected crop.
- The interface displays all detected crops rather than collapsing them into one crop or silently using a previous selection.

## Vertical map integrity

- Rack modules now reference real plant placements and exact tier numbers.
- The map renders crop code and colour inside each occupied rack tier.
- A summary below the map names the crop assigned to each rack tier and to the hanging pot.
- Tall crops above the conservative household-rack height limit remain at ground level.
- Hanging pots use a conservative eligible-crop allow-list and no longer select Caisim by default.
- Hanging and rack assignments do not duplicate calculated plant quantities.
- The rack footprint is included once in occupied-area reporting.

## Sun direction

- The planner now asks which side supplies the strongest direct light.
- The map places the sun outside the plot boundary.
- An arrow points from the light source into the plot.
- The direction is labelled in English or Indonesian.
- A fixed N/E/S/W compass is shown outside the planting area, preventing overlap with crop labels on small plots.

## Deployment impact

No new dependency, database migration, service, or Render setting is required. Render continues to deploy one Python Docker service with the committed static frontend and PostgreSQL database.
