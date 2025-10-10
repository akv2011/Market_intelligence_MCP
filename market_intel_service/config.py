import os
from dataclasses import dataclass


@dataclass
class Settings:
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY", "AIzaSyCVQ_e48n-vDHumYig5h1qx4djXwwVRrlY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")
    use_google_search: bool = os.getenv("USE_GOOGLE_SEARCH", "true").lower() == "true"

    mcp_financial_api_key: str | None = os.getenv("FINANCIAL_DATASETS_API_KEY", "714f22c9-a28c-4a13-8e9b-d4876ae1b5c0")

    db_path: str = os.getenv("DB_PATH", "./market_intel.db")
    context_window: int = int(os.getenv("CONTEXT_WINDOW", "12"))

    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        (
            "You are MarketIntel, an expert market intelligence assistant with real-time web search capabilities. "
            "Answer questions about markets, companies, stocks, financial news, and economic trends. "
            "When users ask for 'latest', 'today', 'current', or time-sensitive information, use your Google Search grounding "
            "to provide up-to-date, accurate market data with proper citations. "
            "Be concise, factual, and cite sources when providing market insights. "
            "For historical or general knowledge, use your training data. "
            "For breaking news or current market conditions, rely on search results."
        ),
    )


settings = Settings()

