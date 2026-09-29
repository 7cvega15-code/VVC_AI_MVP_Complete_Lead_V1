import pytest
import importlib

from src.recommendations.package_recommender import recommend_package
from src.recommendations.addon_recommender import recommend_addons
from src.extraction import inquiry_extractor
from src.extraction.inquiry_extractor import _parse_ai_json


def test_high_score_spark_returns_glamour():
    event_data = {"event_type": "graduation", "wants_prints": False}
    rec = recommend_package(event_data, 100)
    assert rec["recommended"]["tier_name"] == "Glamour"
    assert rec["recommended"]["product_family"] == "The Spark"


def test_high_score_luxe_returns_glamour():
    event_data = {"event_type": "wedding", "wants_prints": True}
    rec = recommend_package(event_data, 100)
    assert rec["recommended"]["tier_name"] == "Glamour"
    assert rec["recommended"]["product_family"] == "The Luxe"


def test_high_score_orbit_returns_glamour_with_override():
    event_data = {"product_family": "The Orbit"}
    rec = recommend_package(event_data, 100)
    assert rec["recommended"]["tier_name"] == "Glamour"
    assert rec["recommended"]["product_family"] == "The Orbit"


def test_recommend_package_never_returns_none_for_valid_family():
    event_data = {"event_type": "school"}
    rec = recommend_package(event_data, 70)
    assert rec["recommended"] is not None
    assert rec["alternative"] is not None
    assert rec["entry"] is not None


def test_no_grand_tier_present():
    # Ensure no returned tier name equals the removed "Grand" value
    event_data = {"product_family": "The Luxe"}
    rec = recommend_package(event_data, 100)
    for key in ("recommended", "alternative", "entry"):
        assert rec[key]["tier_name"] != "Grand"


def test_parse_ai_json_raises_on_malformed():
    malformed = "{not: valid json]"
    with pytest.raises(ValueError):
        _parse_ai_json(malformed)


def test_pipeline_import_does_not_create_openai_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(inquiry_extractor, "load_dotenv", lambda: None)

    def unexpected_client_creation(*args, **kwargs):
        raise AssertionError("OpenAI client should not be created during import")

    monkeypatch.setattr(inquiry_extractor, "OpenAI", unexpected_client_creation)
    importlib.reload(inquiry_extractor)
    importlib.import_module("src.workflows.inquiry_pipeline")


def test_extract_event_info_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(inquiry_extractor, "load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        inquiry_extractor.extract_event_info("A school dance inquiry")
