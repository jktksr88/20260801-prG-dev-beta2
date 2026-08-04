from __future__ import annotations

from datetime import datetime, timedelta, timezone
import html
import re
from typing import Any

from app.ai.fallback import get_ai_service
from app.diary.crop_recognition import aliases_for_crop, normalize_text


TOPICS = {
    "water": ["water", "watering", "dry", "wet", "air", "siram", "kering", "basah", "genang"],
    "pest": ["pest", "aphid", "caterpillar", "bug", "hama", "ulat", "kutu", "serangga"],
    "leaf": [
        "yellow", "leaf", "spot", "spots", "white spot", "wilting", "wilt",
        "daun", "kuning", "bercak", "bintik", "berbintik", "putih", "layu",
    ],
    "growth": [
        "slow", "growth", "seedling", "short", "stunted", "dwarf",
        "lambat", "tumbuh", "bibit", "pendek", "kerdil", "kecil",
    ],
}


def sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value).strip()
    return html.escape(value, quote=False)


def detect_topics(text: str) -> list[str]:
    lower = normalize_text(text)
    return [topic for topic, words in TOPICS.items() if any(normalize_text(word) in lower for word in words)]


def _severity(text: str, topics: list[str]) -> str:
    serious = any(
        key in normalize_text(text)
        for key in ("collapse", "black stem", "severe", "mati", "roboh", "batang hitam", "parah")
    )
    return "attention" if serious else ("watch" if topics else "normal")


def _guidance_for_observation(crop: str, observation: str, language: str) -> tuple[str, str, list[str], str]:
    topics = detect_topics(observation)
    concern = _severity(observation, topics)
    if language == "id":
        if "pest" in topics:
            body = (
                "Kemungkinan ada gangguan hama. Periksa bagian bawah daun dan pucuk pada pagi hari, "
                "catat bentuk serta jumlah hama, lalu singkirkan yang terlihat secara mekanis sebelum "
                "menggunakan perlakuan yang lebih kuat."
            )
            action = f"Periksa bagian bawah daun {crop} hari ini."
        elif "leaf" in topics:
            body = (
                "Bintik, bercak, atau perubahan daun dapat berkaitan dengan kelembapan, percikan air, "
                "sirkulasi udara, nutrisi, atau hama. Periksa apakah gejala menyebar, muncul pada daun muda "
                "atau tua, dan apakah bagian bawah daun juga terdampak."
            )
            action = f"Tandai satu daun {crop} dan bandingkan penyebarannya dalam 2–3 hari."
        elif "growth" in topics:
            body = (
                "Pertumbuhan pendek atau lambat dapat berkaitan dengan cahaya, kepadatan, ruang akar, "
                "kelembapan media, atau tahap pertumbuhan. Bandingkan dengan tanaman sejenis dan hindari "
                "menambah pupuk atau air secara besar-besaran sekaligus."
            )
            action = f"Periksa cahaya, jarak, dan ruang akar {crop} terlebih dahulu."
        elif "water" in topics:
            body = (
                "Masalah kelembapan mungkin terjadi. Periksa media 2–3 cm di bawah permukaan; siram hanya "
                "bila mulai mengering dan pastikan air berlebih dapat keluar."
            )
            action = f"Periksa kelembapan media dan drainase {crop} hari ini."
        else:
            body = (
                "Bandingkan kondisi hari ini dengan kebutuhan cahaya, air, ruang akar, dan tahap pertumbuhan "
                "pada profil tanaman. Hindari beberapa perubahan besar sekaligus."
            )
            action = f"Lakukan satu pemeriksaan sederhana pada {crop} dan perbarui catatan dalam 2–3 hari."
    else:
        if "pest" in topics:
            body = (
                "A pest issue is possible. Inspect leaf undersides and new growth in the morning, record the "
                "shape and approximate count, and remove visible pests mechanically before stronger treatment."
            )
            action = f"Inspect the undersides of {crop} leaves today."
        elif "leaf" in topics:
            body = (
                "White spots or other leaf changes may relate to moisture, water splash, airflow, nutrition, "
                "or pests. Check whether the marks are spreading, which leaf age is affected, and whether leaf "
                "undersides show the same issue."
            )
            action = f"Mark one affected {crop} leaf and compare it again in 2–3 days."
        elif "growth" in topics:
            body = (
                "Short or slow growth may relate to light, crowding, root space, growing-medium moisture, or "
                "growth stage. Compare with similar plants and avoid making a large watering or feeding change at once."
            )
            action = f"Check light, spacing, and root space for {crop} first."
        elif "water" in topics:
            body = (
                "A moisture issue is possible. Check 2–3 cm below the surface; water only when it begins to dry "
                "and confirm that excess water can drain."
            )
            action = f"Check growing-medium moisture and drainage for {crop} today."
        else:
            body = (
                "Compare today’s condition with the crop profile’s light, water, root-space, and growth-stage "
                "guidance. Avoid making several major changes at once."
            )
            action = f"Make one low-risk check on {crop} and update the diary in 2–3 days."
    return body, action, topics, concern


def deterministic_guidance(context: dict[str, Any], text: str, language: str) -> dict[str, Any]:
    crop = context.get("crop_name") or ("tanaman" if language == "id" else "plant")
    weather = context.get("weather", {})
    rain = weather.get("seven_day_rain_mm") if isinstance(weather, dict) else None
    body, action, topics, concern = _guidance_for_observation(str(crop), text, language)
    if rain is not None and rain > 50 and "water" not in topics:
        topics = [*topics, "water"]
    if language == "id":
        response = (
            f"Ini belum merupakan diagnosis pasti untuk {crop}. {body} "
            "Tanda yang memerlukan bantuan lebih lanjut: gejala cepat meluas, batang roboh, bau busuk, "
            "atau kerusakan berat."
        )
    else:
        response = (
            f"This is not a definitive diagnosis for {crop}. {body} "
            "Seek local expert help if symptoms spread rapidly, stems collapse, foul odour develops, or damage becomes severe."
        )
    return {
        "response": response,
        "topics": topics,
        "concern_level": concern,
        "next_action": action,
        "follow_up_date": datetime.now(timezone.utc) + timedelta(days=3) if topics else None,
    }


def observation_for_crop(note: str, crop: dict[str, Any], matched_alias: str | None = None) -> str:
    """Return the clause most closely associated with a named crop."""
    raw = html.unescape(note or "")
    segments = [
        segment.strip()
        for segment in re.split(r"[,;\n]+|\b(?:sedangkan|sementara|while|whereas)\b", raw, flags=re.I)
        if segment.strip()
    ]
    aliases = aliases_for_crop(crop)
    if matched_alias:
        aliases.add(normalize_text(matched_alias))
    for segment in segments:
        normalized = normalize_text(segment)
        if any(f" {alias} " in f" {normalized} " for alias in aliases):
            return segment
    return raw


def deterministic_multi_guidance(
    crop_contexts: list[dict[str, Any]],
    text: str,
    language: str,
) -> dict[str, Any]:
    lines: list[str] = []
    all_topics: list[str] = []
    actions: list[str] = []
    concern_rank = {"normal": 0, "watch": 1, "attention": 2}
    concern = "normal"

    for item in crop_contexts:
        crop_name = str(item.get("crop_name") or item.get("crop", {}).get("slug") or "plant")
        observation = str(item.get("observation") or text)
        body, action, topics, item_concern = _guidance_for_observation(crop_name, observation, language)
        lines.append(f"{crop_name} — {body}")
        actions.append(action)
        for topic in topics:
            if topic not in all_topics:
                all_topics.append(topic)
        if concern_rank[item_concern] > concern_rank[concern]:
            concern = item_concern

    if language == "id":
        intro = "Ini belum merupakan diagnosis pasti. GROE membaca catatan Anda sebagai beberapa tanaman:"
        warning = (
            "Tanda yang memerlukan bantuan lebih lanjut: gejala cepat meluas, batang roboh, bau busuk, "
            "atau kerusakan berat."
        )
        next_action = " ".join(actions)
    else:
        intro = "This is not a definitive diagnosis. GROE read your note as referring to multiple crops:"
        warning = (
            "Seek local expert help if symptoms spread rapidly, stems collapse, foul odour develops, or damage becomes severe."
        )
        next_action = " ".join(actions)

    response = f"{intro}\n\n" + "\n\n".join(lines) + f"\n\n{warning}"
    return {
        "response": response,
        "topics": all_topics,
        "concern_level": concern,
        "next_action": next_action,
        "follow_up_date": datetime.now(timezone.utc) + timedelta(days=3) if all_topics else None,
    }


def clarification_guidance(text: str, language: str, options: list[str]) -> dict[str, Any]:
    topics = detect_topics(text)
    listed = ", ".join(options[:6])
    if language == "id":
        response = "Saya belum bisa memastikan tanaman yang dimaksud. Sebutkan nama tanaman secara alami di catatan berikutnya"
        response += f", misalnya: {listed}." if listed else "."
        action = "Tambahkan nama tanaman agar GROE tidak memberi saran untuk tanaman yang salah."
    else:
        response = "I could not confidently identify which plant you mean. Mention the plant name naturally in your next note"
        response += f", for example: {listed}." if listed else "."
        action = "Add the plant name so GROE does not give advice for the wrong crop."
    return {
        "response": response,
        "topics": topics,
        "concern_level": "clarification",
        "next_action": action,
        "follow_up_date": None,
        "provider_status": "clarification_required",
    }


async def build_diary_response(
    context: dict[str, Any],
    question: str | None,
    entry_text: str,
    language: str,
) -> dict[str, Any]:
    combined = " ".join(filter(None, [entry_text, question]))
    ai = get_ai_service()
    ai_text = await ai.explain_diary(context, question or combined, language)
    fallback = deterministic_guidance(context, combined, language)
    if ai_text:
        fallback["response"] = ai_text
        fallback["provider_status"] = "ai_provider"
    else:
        fallback["provider_status"] = "deterministic_fallback"
    return fallback


async def build_multi_diary_response(
    crop_contexts: list[dict[str, Any]],
    common_context: dict[str, Any],
    question: str | None,
    entry_text: str,
    language: str,
) -> dict[str, Any]:
    combined = " ".join(filter(None, [entry_text, question]))
    ai_context = {**common_context, "crops": crop_contexts, "crop_name": None}
    ai = get_ai_service()
    ai_text = await ai.explain_diary(ai_context, question or combined, language)
    fallback = deterministic_multi_guidance(crop_contexts, combined, language)
    if ai_text:
        fallback["response"] = ai_text
        fallback["provider_status"] = "ai_provider"
    else:
        fallback["provider_status"] = "deterministic_fallback"
    return fallback
