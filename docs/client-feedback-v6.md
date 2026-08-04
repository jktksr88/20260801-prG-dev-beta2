# GROE client-feedback update v6

## Implemented

1. **Location and weather**
   - Indonesian location autocomplete through the server-side Open-Meteo geocoding endpoint.
   - The selected result stores latitude, longitude and elevation.
   - Current temperature, apparent temperature, humidity, rain, cloud cover, wind and a seven-day rainfall summary are retrieved server-side.
   - Visible loading, live-provider and climate-fallback states.
   - Ten-minute in-memory caching reduces repeated external calls.

2. **2D map clarity**
   - Each crop slug now maps to one deterministic colour and one recognizable symbol.
   - The same crop visual is reused on the map, recommendation card and full guide.
   - Legend includes soil, pot, hanging pot, access path, plant stand/rack, trellis and compost.

3. **Pot sizing and capacity**
   - Every container crop returns a GROE recommended diameter, depth and volume.
   - Recommendations are conservatively derived from the crop metadata's minimum container measurements, preferred root depth and preferred spacing.
   - The spatial engine uses the recommended pot diameter as a real footprint and preserves spacing clearance.

4. **Plant recommendation cards**
   - The map is full width and remains the result-page visual hero.
   - Plant cards are a separate section underneath it.
   - Cards show suitability, harvest timing, sun, spacing or pot size and plan quantity.
   - A modal guide shows planting, care, harvest and warning information from the crop metadata.

5. **Internal crop database**
   - The public “50 plants” navigation and landing-page link were removed.
   - The plant endpoint and database remain available internally to the planning engine.

6. **Guest AI diary**
   - Users can open and test the diary without signing in.
   - Guest entries remain in browser local storage.
   - A rate-limited guest-advice endpoint uses the selected plan, crop, weather, growth stage and previous entries.
   - When `OPENAI_API_KEY` is configured, the server uses the OpenAI Responses API.
   - If the key or provider is unavailable, deterministic cautious guidance is returned.
   - Sign-in is still required for saved gardens and cross-device persistence.

## Validation

- 37 tests passed.
- Python compilation passed.
- JavaScript syntax check passed.
- Existing migration and seed structure were unchanged; no database migration is required.
- Production remains one Python-only Docker service. No npm, Node, Vite or separate frontend service is introduced.
