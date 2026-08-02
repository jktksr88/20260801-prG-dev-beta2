# Plant Data Dictionary

## Relational entities

### `species`

Stable botanical identity and taxonomy source. Multiple crop profiles may point to one species.

### `crop_profiles`

A planning-specific form such as tomato versus cherry tomato. Localized names are curated fields, not live translations.

## Core crop-profile fields

- `slug`, `name_en`, `name_id`, `category`, `annual_or_perennial`
- `scientific_name` through the species relationship
- `parameters` — structured environmental, spatial, maintenance and harvest values
- `guidance_en`, `guidance_id` — essential bilingual planting/care/harvest information
- `source_metadata` — taxonomy source, agronomy sources, dates and notes
- `verification_status`, `confidence_level`, `fields_requiring_review`

## Parameter groups

### Environment

Temperature ideal/absolute ranges, elevation bands, sun hours, shade tolerance, heat sensitivity, rainfall/waterlogging and wind sensitivity.

### Space and roots

Mature width/height, spacing, root depth, minimum container dimensions/volume, surface eligibility, trellis eligibility, rack eligibility and allowed tiers.

### Beginner and harvest

Difficulty, maintenance, watering, first-harvest range, harvest frequency, regrowth, succession eligibility, weekly care and beginner success rating.

## Governance states

- `verified`
- `provisionally_sourced`
- `requires_agronomist_review`

The supplied beta seed intentionally uses `requires_agronomist_review` for agronomic measurements. Taxonomy/common-name framing comes from the supplied GROE document; production verification remains explicit.
