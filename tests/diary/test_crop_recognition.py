import pytest

from app.diary.crop_recognition import deterministic_crop_matches, normalize_text, resolve_crop_reference


CROPS = [
    {
        "slug": "kangkung",
        "name_id": "Kangkung",
        "name_en": "Water spinach",
        "alternative_names_id": [],
        "alternative_names_en": [],
    },
    {
        "slug": "caisim",
        "name_id": "Caisim / sawi hijau",
        "name_en": "Choy sum",
        "alternative_names_id": [],
        "alternative_names_en": [],
    },
]


def test_indonesian_suffix_is_normalized():
    assert normalize_text("Caisimnya layu") == "caisim layu"


def test_deterministic_aliases_recognize_bilingual_names():
    assert deterministic_crop_matches(CROPS, "caisimnya layu")[0].crop["slug"] == "caisim"
    assert deterministic_crop_matches(CROPS, "my choy sum is wilting")[0].crop["slug"] == "caisim"
    assert deterministic_crop_matches(CROPS, "sawi hijaunya lambat tumbuh")[0].crop["slug"] == "caisim"


@pytest.mark.asyncio
async def test_recognition_never_falls_back_to_previously_selected_crop():
    result = await resolve_crop_reference(CROPS, "caisimnya layu", "id")
    assert result["crop"]["slug"] == "caisim"
    assert result["method"] == "exact_alias"
    assert result["clarification_needed"] is False


@pytest.mark.asyncio
async def test_unnamed_plant_requests_clarification():
    result = await resolve_crop_reference(CROPS, "tanamannya layu", "id")
    assert result["crop"] is None
    assert result["clarification_needed"] is True
    assert "Kangkung" in result["options"]


def test_common_indonesian_spelling_variants_are_resolved():
    crops = [
        {
            "slug": "pakcoy",
            "name_id": "Pakcoy",
            "name_en": "Pak choi",
            "alternative_names_id": [],
            "alternative_names_en": [],
        },
        *CROPS,
    ]
    matches = deterministic_crop_matches(crops, "pokcoy pendek, caisin berbintik putih")
    assert [match.crop["slug"] for match in matches[:2]] == ["pakcoy", "caisim"]


@pytest.mark.asyncio
async def test_multiple_explicit_crops_are_kept_separate_without_clarification():
    crops = [
        {
            "slug": "pakcoy",
            "name_id": "Pakcoy",
            "name_en": "Pak choi",
            "alternative_names_id": [],
            "alternative_names_en": [],
        },
        *CROPS,
    ]
    result = await resolve_crop_reference(crops, "pokcoy pendek ya, caisin berbintik putih", "id")
    assert [crop["slug"] for crop in result["crops"]] == ["pakcoy", "caisim"]
    assert result["crop"] is None
    assert result["clarification_needed"] is False
    assert result["method"] == "deterministic_multi_crop"
