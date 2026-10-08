from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional, Any

from fastmcp import Client

from .config import settings

MCP_SERVER = Path(__file__).resolve().parent.parent / "mcp-server-main" / "server.py"
UNAVAILABLE = "The answer service is unavailable right now. Try again later."
log = logging.getLogger(__name__)

Message = Dict[str, str]
class GeminiClient:
    """Gemini client with Google Search grounding and MCP financial tool calling."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        try:
            from google import genai
            from google.genai import types
            self.genai = genai
            self.types = types
            # free-tier keys often get 503 "high demand", so those are retried with backoff;
            # 429 is not, because the free tier's limit is per day and a retry only spends more of it
            retry = types.HttpRetryOptions(attempts=5, initial_delay=1.0, max_delay=16.0, http_status_codes=[408, 500, 502, 503, 504])
            self.client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(retry_options=retry))
        except ImportError:
            raise ImportError("google-genai package is required")
    
    def _convert_messages(self, messages: List[Message]) -> tuple:
        system_instruction = None
        user_messages = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_instruction = content
            elif role == "user":
                user_messages.append(content)
        
        combined_message = "\n\n".join(user_messages) if user_messages else "Hello"
        return system_instruction, combined_message
    
    async def extract_ticker_with_gemini(self, user_query: str) -> Dict[str, Any]:
        extraction_prompt = f"""Analyze this query and extract ticker info as JSON:

Query: "{user_query}"

Return JSON:
{{
  "ticker": "TICKER or null",
  "company_name": "name or null",
  "needs_financial_data": true/false,
  "query_type": "stock_price|crypto_price|company_news|financial_statements|general_market"
}}

Examples:
- "Tesla stock" -> {{"ticker": "TSLA", "needs_financial_data": true, "query_type": "stock_price"}}
- "Bitcoin price" -> {{"ticker": "BTC-USD", "needs_financial_data": true, "query_type": "crypto_price"}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=extraction_prompt,
                config={"temperature": 0.1, "response_mime_type": "application/json"}
            )
            parsed = json.loads(response.text)
            # Ensure we return a dict, not a list
            if isinstance(parsed, list):
                parsed = parsed[0] if parsed else {}
            return parsed
        except Exception:
            log.warning("ticker extraction failed", exc_info=True)
            return {"ticker": None, "needs_financial_data": False, "query_type": "general_market"}
    
    async def call_mcp_financial_tool(self, ticker: str, query_type: str) -> str:
        try:
            tool_mapping = {
                "stock_price": "get_current_stock_price",
                "crypto_price": "get_current_crypto_price",
                "company_news": "get_company_news",
                "financial_statements": "get_income_statements",
            }
            
            tool_name = tool_mapping.get(query_type, "get_current_stock_price")

            async with Client(MCP_SERVER, timeout=30) as client:
                result = await client.call_tool(tool_name, {"ticker": ticker}, raise_on_error=False)
            return result.content[0].text if result.content else "No data"
        except Exception:
            log.exception("market data call failed")
            return "Market data is unavailable for this question."
    
    async def generate(self, messages: List[Message], model: Optional[str] = None) -> str:
        system_instruction, user_query = self._convert_messages(messages)
        
        analysis = await self.extract_ticker_with_gemini(user_query)
        
        financial_data = ""
        if analysis.get("needs_financial_data") and analysis.get("ticker"):
            ticker = analysis["ticker"]
            query_type = analysis["query_type"]
            financial_data = await self.call_mcp_financial_tool(ticker, query_type)
        
        enhanced_prompt = f"""You are MarketIntel AI assistant.

USER QUERY: {user_query}

ANALYSIS: {json.dumps(analysis, indent=2)}

FINANCIAL DATA: {financial_data if financial_data else "No data"}

Instructions:
1. Use financial data from MCP server if available
2. Use Google Search for latest news/context
3. Combine both sources
4. Cite sources
5. Be concise

Provide response:"""

        config = {"temperature": 0.3}
        if system_instruction:
            config["system_instruction"] = system_instruction
        if settings.use_google_search:
            config["tools"] = [{"google_search": {}}]
        
        try:
            response = self.client.models.generate_content(
                model=model or settings.gemini_model,
                contents=enhanced_prompt,
                config=config
            )
            return response.text
        except Exception:
            # provider errors can quote the API key, so callers only get a fixed message
            log.exception("Gemini call failed")
            return UNAVAILABLE
    
    async def generate_stream(self, messages: List[Message], model: Optional[str] = None) -> AsyncIterator[str]:
        system_instruction, user_query = self._convert_messages(messages)
        
        analysis = await self.extract_ticker_with_gemini(user_query)
        yield f"Analyzing...\n"
        
        financial_data = ""
        if analysis.get("needs_financial_data") and analysis.get("ticker"):
            ticker = analysis["ticker"]
            query_type = analysis["query_type"]
            yield f"Fetching {ticker} data...\n\n"
            financial_data = await self.call_mcp_financial_tool(ticker, query_type)
        
        enhanced_prompt = f"""You are MarketIntel AI assistant.

USER QUERY: {user_query}

ANALYSIS: {json.dumps(analysis, indent=2)}

FINANCIAL DATA: {financial_data if financial_data else "No data"}

Instructions:
1. Use financial data if available
2. Use Google Search for latest news
3. Combine sources
4. Cite sources

Provide response:"""

        config = {"temperature": 0.3}
        if system_instruction:
            config["system_instruction"] = system_instruction
        if settings.use_google_search:
            config["tools"] = [{"google_search": {}}]
        
        try:
            for chunk in self.client.models.generate_content_stream(
                model=model or settings.gemini_model,
                contents=enhanced_prompt,
                config=config
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
        except Exception:
            log.exception("Gemini stream failed")
            yield f"\n\n{UNAVAILABLE}"


def make_llm() -> GeminiClient:
    return GeminiClient()
