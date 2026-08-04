from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import html
import re
import unicodedata
from typing import Any

from app.ai.fallback import get_ai_service


# Curated aliases supplement the bilingual crop metadata. They are intentionally
# limited to names, spelling variants and widely used market terms; they do not
# introduce agronomic facts.
CURATED_ALIASES: dict[str, tuple[str, ...]] = {
    "kangkung": ("water spinach", "morning glory vegetable"),
    "bayam-hijau": ("bayam", "amaranth", "green spinach"),
    "pakcoy": ("pak choi", "bok choy", "bok choi", "sawi sendok"),
    "caisim": ("caisim", "caysim", "choy sum", "choysum", "choi sum", "sawi hijau", "sawi caisim"),
    "kailan": ("kai lan", "gai lan", "chinese broccoli"),
    "kubis": ("kol",),
    "daun-bawang": ("spring onion", "green onion", "scallion"),
    "kenikir": ("ulam raja", "cosmos"),
    "tomat-ceri": ("cherry tomatoes",),
    "cabai-rawit": ("cabe rawit", "bird eye chili", "birds eye chili", "chili padi", "cili padi"),
    "cabai-merah": ("cabe merah", "red chilli", "red chile"),
    "paprika": ("bell pepper", "capsicum"),
    "terong": ("aubergine",),
    "mentimun": ("timun",),
    "pare": ("paria",),
    "kacang-panjang": ("long bean", "yard long bean"),
    "oyong": ("gambas", "angled gourd", "ridge gourd"),
    "labu-kuning": ("labu", "squash"),
    "labu-siam": ("jipang",),
    "stroberi": ("strawberries",),
    "pepaya-kerdil": ("pepaya", "papaya"),
    "kemangi": ("lemon basil", "indonesian basil"),
    "basil": ("sweet basil",),
    "mint": ("spearmint",),
    "ketumbar": ("coriander", "cilantro"),
    "serai": ("sereh", "lemon grass"),
    "kucai": ("chives",),
    "jeruk-purut": ("kaffir lime", "makrut lime"),
    "lobak-putih": ("daikon", "white radish"),
    "bit": ("beet", "beet root"),
    "ubi-jalar": ("sweetpotato",),
    "bawang-merah": ("shallots",),
    "bawang-putih": ("garlic bulb",),
}


@dataclass(frozen=True)
class CropMatch:
    crop: dict[str, Any]
    confidence: float
    matched_alias: str
    method: str


def _strip_marks(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )


def normalize_text(value: str) -> str:
    value = html.unescape(value or "")
    value = _strip_marks(value).lower().replace("’", "'")
    tokens = re.findall(r"[a-z0-9]+", value)
    normalized: list[str] = []
    for token in tokens:
        # Indonesian possessive/emphatic suffixes commonly attach directly to
        # crop names: caisimnya, kangkungku, cabaimu.
        for suffix in ("nya", "ku", "mu"):
            if token.endswith(suffix) and len(token) - len(suffix) >= 4:
                token = token[: -len(suffix)]
                break
        normalized.append(token)
    return " ".join(normalized)


def _name_parts(value: str | None) -> set[str]:
    if not value:
        return set()
    cleaned = re.sub(r"\([^)]*\)", " ", value)
    parts = {cleaned}
    parts.update(part.strip() for part in re.split(r"[/;|]", cleaned) if part.strip())
    return {normalize_text(part) for part in parts if normalize_text(part)}


def aliases_for_crop(crop: dict[str, Any]) -> set[str]:
    aliases: set[str] = set()
    aliases.update(_name_parts(crop.get("name_id")))
    aliases.update(_name_parts(crop.get("name_en")))
    aliases.update(_name_parts(str(crop.get("slug", "")).replace("-", " ")))
    aliases.update(_name_parts(crop.get("scientific_name")))
    for key in ("alternative_names_id", "alternative_names_en"):
        for value in crop.get(key) or []:
            aliases.update(_name_parts(str(value)))
    for value in CURATED_ALIASES.get(str(crop.get("slug")), ()):
        aliases.update(_name_parts(value))
    return {alias for alias in aliases if len(alias) >= 3}


def _ngrams(tokens: list[str], size: int) -> list[str]:
    if size <= 0 or len(tokens) < size:
        return []
    return [" ".join(tokens[index : index + size]) for index in range(len(tokens) - size + 1)]


def _score_alias(normalized_note: str, alias: str) -> tuple[float, str] | None:
    if not alias:
        return None
    padded_note = f" {normalized_note} "
    if f" {alias} " in padded_note:
        return 0.99, "exact_alias"

    note_tokens = normalized_note.split()
    alias_tokens = alias.split()
    if len(alias) < 4:
        return None

    candidates = note_tokens if len(alias_tokens) == 1 else _ngrams(note_tokens, len(alias_tokens))
    best = max((SequenceMatcher(None, candidate, alias).ratio() for candidate in candidates), default=0.0)
    threshold = 0.90 if len(alias) <= 5 else 0.86
    if best >= threshold:
        return round(0.70 + (best - threshold) * 1.4, 3), "fuzzy_alias"
    return None


def deterministic_crop_matches(crops: list[dict[str, Any]], note: str) -> list[CropMatch]:
    normalized_note = normalize_text(note)
    if not normalized_note:
        return []
    matches: list[CropMatch] = []
    for crop in crops:
        best: tuple[float, str, str] | None = None
        for alias in aliases_for_crop(crop):
            result = _score_alias(normalized_note, alias)
            if result and (best is None or result[0] > best[0] or (result[0] == best[0] and len(alias) > len(best[1]))):
                best = (result[0], alias, result[1])
        if best:
            matches.append(CropMatch(crop=crop, confidence=best[0], matched_alias=best[1], method=best[2]))
    return sorted(matches, key=lambda match: (-match.confidence, -len(match.matched_alias), str(match.crop.get("slug"))))


def _crop_label(crop: dict[str, Any], language: str) -> str:
    return str(crop.get("name_id") if language == "id" else crop.get("name_en") or crop.get("name_id") or crop.get("slug"))


async def resolve_crop_reference(
    crops: list[dict[str, Any]],
    note: str,
    language: str,
) -> dict[str, Any]:
    """Resolve the crop mentioned in a free-form bilingual diary entry.

    Deterministic metadata matching runs first. The optional AI provider is only
    asked to disambiguate or recover a crop when deterministic matching is not
    decisive. Any AI result is verified against crops in the selected plan.
    """
    crops = [crop for crop in crops if crop.get("slug")]
    matches = deterministic_crop_matches(crops, note)
    strong = [match for match in matches if match.confidence >= 0.88]

    if len(strong) == 1:
        match = strong[0]
        return {
            "crop": match.crop,
            "confidence": match.confidence,
            "method": match.method,
            "matched_alias": match.matched_alias,
            "clarification_needed": False,
            "options": [],
        }

    # More than one explicitly named crop is not silently collapsed to one.
    if len(strong) > 1:
        ai = get_ai_service()
        ai_result = await ai.recognize_crop(crops, note, language)
        verified = _verify_ai_result(ai_result, crops)
        if verified and float(verified["confidence"]) >= 0.82:
            return {
                "crop": verified["crop"],
                "confidence": float(verified["confidence"]),
                "method": "ai_disambiguation",
                "matched_alias": None,
                "clarification_needed": False,
                "options": [],
            }
        return {
            "crop": None,
            "confidence": strong[0].confidence,
            "method": "ambiguous_multiple_crops",
            "matched_alias": None,
            "clarification_needed": True,
            "options": [_crop_label(match.crop, language) for match in strong[:4]],
        }

    # A single high-quality fuzzy match is safe when no close competitor exists.
    if matches and matches[0].confidence >= 0.78:
        runner_up = matches[1].confidence if len(matches) > 1 else 0.0
        if matches[0].confidence - runner_up >= 0.08:
            match = matches[0]
            return {
                "crop": match.crop,
                "confidence": match.confidence,
                "method": match.method,
                "matched_alias": match.matched_alias,
                "clarification_needed": False,
                "options": [],
            }

    ai = get_ai_service()
    ai_result = await ai.recognize_crop(crops, note, language)
    verified = _verify_ai_result(ai_result, crops)
    if verified and float(verified["confidence"]) >= 0.72:
        return {
            "crop": verified["crop"],
            "confidence": float(verified["confidence"]),
            "method": "ai_recognition",
            "matched_alias": None,
            "clarification_needed": False,
            "options": [],
        }

    options = [_crop_label(crop, language) for crop in crops[:6]]
    return {
        "crop": None,
        "confidence": 0.0,
        "method": "unresolved",
        "matched_alias": None,
        "clarification_needed": True,
        "options": options,
    }


def _verify_ai_result(result: dict[str, Any] | None, crops: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not result:
        return None
    slug = str(result.get("slug") or "").strip()
    crop = next((candidate for candidate in crops if candidate.get("slug") == slug), None)
    if not crop:
        return None
    try:
        confidence = max(0.0, min(1.0, float(result.get("confidence", 0.0))))
    except (TypeError, ValueError):
        return None
    return {"crop": crop, "confidence": confidence}
