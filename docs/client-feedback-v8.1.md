# GROE v8.1 — Diary recognition and map-truth patch

## Free-text bilingual crop recognition

The diary remains a free-writing experience. No crop selector was added.

Recognition runs in this order:

1. Deterministic matching against crops in the selected plan.
2. Bilingual names, slash-separated names, alternative names, scientific names and curated spelling variants.
3. Indonesian attached-suffix normalization, including examples such as `caisimnya`, `kangkungku` and `cabaimu`.
4. Optional AI recognition only when deterministic matching is uncertain.
5. Verification that any AI-selected slug exists in the current plan.
6. A short clarification response when the plant remains unclear. GROE never silently falls back to the previously opened crop.

Examples recognized deterministically:

- `caisimnya layu`
- `sawi hijaunya lambat tumbuh`
- `my choy sum is wilting`

The diary entry displays a subtle detected-plant badge. If no crop can be resolved, the entry asks the user to mention one of the crops already in the garden.

## Hanging-pot map truth

A hanging pot is now one real crop placement, not a decorative module added on top of ground-pot quantities.

- One eligible container allocation is converted to `structure_type: hanging_pot`.
- Its vertical-module metadata references the same `placement_id`.
- The map renders the crop's standard colour and code inside the hanging pot.
- The separate decorative hanging-pot symbol was removed.
- The hanging-pot legend is enabled only when an actual hanging-pot placement exists.
- Container footprint and quantity accounting remain unchanged and conservative.

## Deployment

No migration, dependency, Dockerfile, database or Render setting change is required. The patch adds versioned static assets `app.v8.1.js` and `styles.v8.1.css` and updates the build marker to `8.1.0`.
