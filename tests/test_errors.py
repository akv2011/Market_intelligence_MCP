import asyncio

from market_intel_service.llm import UNAVAILABLE, GeminiClient

SECRET = "AIzaFAKE-key-that-must-not-leak"


class Failing:
    def generate_content(self, **_):
        raise RuntimeError(f"403 PERMISSION_DENIED. Consumer 'api_key:{SECRET}' has been suspended.")

    generate_content_stream = generate_content


def client() -> GeminiClient:
    c = GeminiClient(api_key="unused")
    c.client = type("Stub", (), {"models": Failing()})()
    return c


def test_a_provider_error_never_reaches_the_caller():
    text = asyncio.run(client().generate([{"role": "user", "content": "NVIDIA price?"}]))
    assert text == UNAVAILABLE and SECRET not in text


def test_a_streamed_provider_error_never_reaches_the_caller():
    async def collect():
        return "".join([c async for c in client().generate_stream([{"role": "user", "content": "NVIDIA price?"}])])

    text = asyncio.run(collect())
    assert UNAVAILABLE in text and SECRET not in text


class Empty:
    def generate_content(self, **_):
        return type("Response", (), {"text": None, "candidates": []})()


def test_an_empty_model_reply_becomes_the_fixed_message():
    c = GeminiClient(api_key="unused")
    c.client = type("Stub", (), {"models": Empty()})()
    assert asyncio.run(c.generate([{"role": "user", "content": "NVIDIA price?"}])) == UNAVAILABLE


def test_without_search_the_model_is_told_not_to_call_tools(monkeypatch):
    from market_intel_service import llm

    monkeypatch.setattr(llm.settings, "use_google_search", False)
    config = llm._config("You are MarketIntel. Use your Google Search grounding.")
    assert "tools" not in config and llm.NO_SEARCH in config["system_instruction"]
