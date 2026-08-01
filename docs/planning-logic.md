# Deterministic Planning Logic

## Philosophy

The engine asks what is feasible and which modifications improve success. Limited area normally changes quantity, density, crop profile or spatial strategy; it does not block the full journey. `not_suitable` is reserved for genuine physical or severe environmental conflicts.

## Pipeline

1. Validate dimensions and polygon geometry.
2. Calculate plot area and reserve an access strip only when the space is large enough.
3. Combine Open-Meteo conditions with a broad Indonesian city/elevation fallback.
4. Score every active crop across climate, sun, space, root zone, surface, maintenance, goal, beginner fit and water access.
5. Apply hard constraints.
6. Rank candidates independently for Easy Start, Fast Harvest and Balanced Kitchen.
7. Enforce crop-set diversity where alternatives exist.
8. Allocate provisional quantities from usable-area budgets.
9. Pack every footprint inside the actual polygon.
10. Reduce unplaceable quantities and return reason-coded adjustments.

## Hard constraints

- Absolute container depth below crop minimum.
- Crop footprint cannot fit usable geometry.
- Invalid surface eligibility.
- Required trellis/support unavailable.
- Severe absolute-temperature incompatibility.
- Invalid or self-intersecting polygon.
- Placement outside the polygon or overlapping another reserved footprint.

## Soft adjustments

- Quantity reduction.
- Light limitation note.
- Climate protection or alternative.
- Care-commitment stretch.
- Water-access warning.
- Compact/off-site compost instead of forcing equipment into a small space.

## Plan objective functions

### Easy Start

Higher weight for overall feasibility, beginner success, lower maintenance, shorter cycles and smaller footprints.

### Fast Harvest

Higher weight for time to first harvest, regrowth and succession eligibility.

### Balanced Kitchen

Actively attempts category coverage across leafy vegetables, herbs, fruiting crops and roots while retaining feasibility.

## Spatial method

The beta uses deterministic scan-line packing over the usable Shapely polygon. Every crop footprint is tested with `polygon.covers()`. Trellised vines use a narrower depth representation and create a separate support module. Taller crops are inserted first from the selected sun edge. The output contains real metre coordinates and dimensions for SVG rendering.

This is intentionally deterministic and testable. It is not presented as a mathematically perfect global optimum.
