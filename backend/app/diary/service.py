from __future__ import annotations
import html, re
from datetime import datetime, timedelta, timezone
from typing import Any
from app.ai.fallback import get_ai_service

TOPICS = {
    "water": ["water","watering","dry","wet","air","siram","kering","basah","genang"],
    "pest": ["pest","aphid","caterpillar","bug","hama","ulat","kutu"],
    "leaf": ["yellow","leaf","spot","wilting","daun","kuning","bercak","layu"],
    "growth": ["slow","growth","seedling","lambat","tumbuh","bibit"],
}

def sanitize_text(value: str | None) -> str | None:
    if value is None: return None
    value=re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value).strip()
    return html.escape(value, quote=False)

def detect_topics(text: str) -> list[str]:
    lower=text.lower()
    return [topic for topic,words in TOPICS.items() if any(w in lower for w in words)]

def deterministic_guidance(context: dict[str,Any], text: str, language: str) -> dict[str,Any]:
    topics=detect_topics(text)
    serious=any(k in text.lower() for k in ["collapse","black stem","severe","mati","roboh","batang hitam","parah"])
    concern="attention" if serious else ("watch" if topics else "normal")
    crop=context.get("crop_name") or ("tanaman" if language=="id" else "plant")
    weather=context.get("weather",{})
    rain=weather.get("seven_day_rain_mm")
    if language=="id":
        intro=f"Ini belum merupakan diagnosis pasti untuk {crop}."
        if "water" in topics or (rain is not None and rain>50):
            body="Kemungkinan masalah berkaitan dengan kelembapan. Periksa media 2–3 cm di bawah permukaan; siram hanya bila mulai mengering dan pastikan air dapat keluar."
            action="Periksa kelembapan media dan lubang drainase hari ini."
        elif "pest" in topics:
            body="Kemungkinan ada gangguan hama. Periksa bagian bawah daun dan pucuk pada pagi hari, lalu singkirkan hama yang terlihat dengan cara mekanis sebelum memakai perlakuan yang lebih kuat."
            action="Foto tidak digunakan dalam beta; catat bentuk, lokasi, dan jumlah hama yang terlihat."
        elif "leaf" in topics:
            body="Perubahan daun dapat dipicu air, cahaya, nutrisi, atau hama. Mulai dari pemeriksaan paling rendah risiko: kelembapan, drainase, cahaya harian, dan bagian bawah daun."
            action="Catat apakah gejala muncul pada daun tua, daun muda, atau seluruh tanaman."
        else:
            body="Bandingkan kondisi hari ini dengan kebutuhan cahaya, air, ruang akar, dan tahap pertumbuhan pada profil tanaman. Hindari perubahan besar sekaligus."
            action="Lakukan satu pemeriksaan sederhana dan tambahkan pembaruan dalam 2–3 hari."
        response=f"{intro} {body} Tanda yang memerlukan bantuan lebih lanjut: layu cepat meluas, batang roboh, bau busuk, atau kerusakan berat."
    else:
        intro=f"This is not a definitive diagnosis for {crop}."
        if "water" in topics or (rain is not None and rain>50):
            body="A moisture issue is possible. Check 2–3 cm below the surface; water only when it begins to dry and confirm that excess water can drain."
            action="Check growing-medium moisture and drainage holes today."
        elif "pest" in topics:
            body="A pest issue is possible. Inspect leaf undersides and new growth in the morning, then remove visible pests mechanically before using stronger treatments."
            action="Photo analysis is not used in this beta; record the pest shape, location and approximate count."
        elif "leaf" in topics:
            body="Leaf changes can come from water, light, nutrition or pests. Start with low-risk checks: moisture, drainage, daily light and leaf undersides."
            action="Record whether symptoms begin on old leaves, new leaves or the whole plant."
        else:
            body="Compare today’s condition with the crop profile’s light, water, root-space and growth-stage guidance. Avoid making several major changes at once."
            action="Make one low-risk check and add an update in 2–3 days."
        response=f"{intro} {body} Escalation signs include rapidly spreading wilt, stem collapse, foul odour or severe damage."
    return {"response":response,"topics":topics,"concern_level":concern,"next_action":action,"follow_up_date":datetime.now(timezone.utc)+timedelta(days=3) if topics else None}

async def build_diary_response(context: dict[str,Any], question: str|None, entry_text: str, language: str) -> dict[str,Any]:
    combined=" ".join(filter(None,[entry_text,question]))
    ai=get_ai_service()
    ai_text=await ai.explain_diary(context,question or combined,language)
    fallback=deterministic_guidance(context,combined,language)
    if ai_text:
        fallback["response"]=ai_text
        fallback["provider_status"]="ai_provider"
    else:
        fallback["provider_status"]="deterministic_fallback"
    return fallback
