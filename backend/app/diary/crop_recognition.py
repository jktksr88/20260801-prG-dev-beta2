from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import html
import re
import unicodedata
from typing import Any

from app.ai.fallback import get_ai_service


# Curated aliases supplement the bilingual crop metadata. They are limited to
# names, spelling variants and common market terms; they do not add agronomic
# claims. Add aliases here rather than asking the language model to guess.
CURATED_ALIASES: dict[str, tuple[str, ...]] = {
    "kangkung": ("water spinach", "morning glory vegetable"),
    "bayam-hijau": ("bayam", "amaranth", "green spinach"),
    "pakcoy": (
        "pak choi",
        "pak choy",
        "pak coy",
        "pakcoy",
        "pokcoy",
        "pok coy",
        "pok choy",
        "bok choy",
        "bok choi",
        "sawi sendok",
    ),
    "caisim": (
        "caisim",
        "caisin",
        "caesim",
        "caysim",
        "choy sum",
        "choysum",
        "choi sum",
        "sawi hijau",
        "sawi ijo",
        "sawi caisim",
    ),
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
    position: int


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
        # crop names: caisimnya, kangkungku, pakcoymu.
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


def _ngrams(tokens: list[str], size: int) -> list[tuple[str, int]]:
    if size <= 0 or len(tokens) < size:
        return []
    output: list[tuple[str, int]] = []
    for index in range(len(tokens) - size + 1):
        phrase = " ".join(tokens[index : index + size])
        position = len(" ".join(tokens[:index])) + (1 if index else 0)
        output.append((phrase, position))
    return output


def _score_alias(normalized_note: str, alias: str) -> tuple[float, str, int] | None:
    if not alias:
        return None
    padded_note = f" {normalized_note} "
    marker = f" {alias} "
    exact_index = padded_note.find(marker)
    if exact_index >= 0:
        return 0.99, "exact_alias", max(0, exact_index - 1)

    note_tokens = normalized_note.split()
    alias_tokens = alias.split()
    if len(alias) < 4:
        return None

    candidates = (
        [(token, len(" ".join(note_tokens[:index])) + (1 if index else 0)) for index, token in enumerate(note_tokens)]
        if len(alias_tokens) == 1
        else _ngrams(note_tokens, len(alias_tokens))
    )
    best_ratio = 0.0
    best_position = 10**9
    for candidate, position in candidates:
        ratio = SequenceMatcher(None, candidate, alias).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_position = position
    threshold = 0.90 if len(alias) <= 5 else 0.86
    if best_ratio >= threshold:
        return round(0.70 + (best_ratio - threshold) * 1.4, 3), "fuzzy_alias", best_position
    return None


def deterministic_crop_matches(crops: list[dict[str, Any]], note: str) -> list[CropMatch]:
    normalized_note = normalize_text(note)
    if not normalized_note:
        return []
    matches: list[CropMatch] = []
    for crop in crops:
        best: tuple[float, str, str, int] | None = None
        for alias in aliases_for_crop(crop):
            result = _score_alias(normalized_note, alias)
            if not result:
                continue
            candidate = (result[0], alias, result[1], result[2])
            if best is None:
                best = candidate
            elif candidate[0] > best[0]:
                best = candidate
            elif candidate[0] == best[0] and len(candidate[1]) > len(best[1]):
                best = candidate
        if best:
            matches.append(
                CropMatch(
                    crop=crop,
                    confidence=best[0],
                    matched_alias=best[1],
                    method=best[2],
                    position=best[3],
                )
            )
    return sorted(
        matches,
        key=lambda match: (match.position, -match.confidence, -len(match.matched_alias), str(match.crop.get("slug"))),
    )


def _crop_label(crop: dict[str, Any], language: str) -> str:
    return str(crop.get("name_id") if language == "id" else crop.get("name_en") or crop.get("name_id") or crop.get("slug"))


def _match_payload(match: CropMatch) -> dict[str, Any]:
    return {
        "crop": match.crop,
        "confidence": match.confidence,
        "method": match.method,
        "matched_alias": match.matched_alias,
        "position": match.position,
    }


def _result_from_matches(matches: list[CropMatch]) -> dict[str, Any]:
    crops = [match.crop for match in matches]
    primary = crops[0] if len(crops) == 1 else None
    confidence = min((match.confidence for match in matches), default=0.0)
    method = matches[0].method if len(matches) == 1 else "deterministic_multi_crop"
    return {
        "crop": primary,
        "crops": crops,
        "matches": [_match_payload(match) for match in matches],
        "confidence": confidence,
        "method": method,
        "matched_alias": matches[0].matched_alias if len(matches) == 1 else None,
        "clarification_needed": False,
        "options": [],
    }


async def resolve_crop_reference(
    crops: list[dict[str, Any]],
    note: str,
    language: str,
) -> dict[str, Any]:
    """Resolve one or more crops in a free-form bilingual diary entry.

    Straightforward names and common spelling variants are resolved
    deterministically. The optional AI provider is used only when deterministic
    matching is uncertain, and every AI result is verified against crops in the
    selected plan. Multiple explicitly named crops remain multiple crops.
    """
    crops = [crop for crop in crops if crop.get("slug")]
    matches = deterministic_crop_matches(crops, note)
    strong = [match for match in matches if match.confidence >= 0.88]

    if strong:
        return _result_from_matches(strong[:6])

    # A single high-quality fuzzy match is safe when no close competitor exists.
    if matches and matches[0].confidence >= 0.78:
        runner_up = matches[1].confidence if len(matches) > 1 else 0.0
        if matches[0].confidence - runner_up >= 0.08:
            return _result_from_matches([matches[0]])

    ai = get_ai_service()
    ai_result = await ai.recognize_crops(crops, note, language)
    verified = _verify_ai_results(ai_result, crops)
    if verified:
        verified_matches = [
            CropMatch(
                crop=item["crop"],
                confidence=item["confidence"],
                matched_alias="",
                method="ai_recognition",
                position=index,
            )
            for index, item in enumerate(verified)
            if item["confidence"] >= 0.72
        ]
        if verified_matches:
            return _result_from_matches(verified_matches)

    options = [_crop_label(crop, language) for crop in crops[:6]]
    return {
        "crop": None,
        "crops": [],
        "matches": [],
        "confidence": 0.0,
        "method": "unresolved",
        "matched_alias": None,
        "clarification_needed": True,
        "options": options,
    }


def _verify_ai_results(
    results: list[dict[str, Any]] | dict[str, Any] | None,
    crops: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not results:
        return []
    if isinstance(results, dict):
        results = [results]
    if not isinstance(results, list):
        return []
    verified: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            continue
        slug = str(result.get("slug") or "").strip()
        if not slug or slug in seen:
            continue
        crop = next((candidate for candidate in crops if candidate.get("slug") == slug), None)
        if not crop:
            continue
        try:
            confidence = max(0.0, min(1.0, float(result.get("confidence", 0.0))))
        except (TypeError, ValueError):
            continue
        verified.append({"crop": crop, "confidence": confidence})
        seen.add(slug)
    return verified
