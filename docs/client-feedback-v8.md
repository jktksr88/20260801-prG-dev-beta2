# GROE Client Feedback v8

## 1. Location and weather

The first planner step now provides a typed location field with a selectable dropdown. Major Indonesian cities are available from a built-in fallback immediately, while the backend also searches Open-Meteo. Selecting a location stores coordinates and retrieves temperature, humidity, rain, wind, apparent temperature and update time. Failure states remain usable through broad climate fallback.

## 2. Standardized 2D visualization

Every crop uses one deterministic two-letter code and colour. The same identity appears on the map, plant key, card and guide. The map includes a separate infrastructure legend for direct soil, pot, hanging pot, access path, stand/rack, trellis and compost.

## 3. Pot sizing

Container plans expose minimum and recommended diameter, depth and volume. The layout engine uses the recommended pot diameter in each spatial footprint. The selected plan also presents a grouped pot inventory.

## 4. Plant cards

The 2D map is the first and largest result section. Plant cards are presented separately beneath it, using an editorial card system with suitability, harvest time, sunlight, ideal pot or spacing, quantity and a full guide modal.

## 5. Hidden crop database

There is no crop-catalogue item in public navigation. The 50 profiles remain available only as structured planner, layout and diary metadata.

## 6. Guest AI diary

The sign-in control is removed from the beta interface. Users can save plans and diary entries in the current browser. Diary questions are sent to the guest-advice endpoint, which uses the configured OpenAI provider when available and cautious deterministic guidance otherwise.
