# Market Intelligence AI Backend Service

AI-powered market intelligence backend service with real-time financial data integration and web search capabilities.

## Overview

Backend service providing intelligent market analysis through:
- MCP (Model Context Protocol) server integration for financial data
- Google Gemini AI with real-time web search grounding
- RESTful API endpoints (streaming and non-streaming)
- Conversational context memory using SQLite
- Two-stage AI pipeline: ticker extraction and data synthesis

## Features

- MCP Financial Server Integration: Real-time stock prices, crypto data, company news, financial statements
- HTTP API Endpoints:
  - POST /query - Non-streaming JSON responses
  - POST /query/stream - Server-Sent Events streaming for real-time chat
  - GET /health - Health check endpoint
- Context Memory: SQLite-based conversation history with session management
- Google Gemini AI: `gemini-3.8-flash` by default (set `GEMINI_MODEL` to change it) with Google Search grounding
- Errors: provider and tool failures are logged on the server; callers get a fixed message, because provider error text can quote the API key
- Two-Stage Intelligence:
  - Stage 1: Extract ticker symbols and query type
  - Stage 2: Fetch MCP financial data + Google Search + AI synthesis

## MCP server

`mcp-server-main/` is an MCP server over the Financial Datasets API, adapted from [financial-datasets/mcp-server](https://github.com/financial-datasets/mcp-server) (MIT, see `mcp-server-main/LICENSE`). It runs on FastMCP 4 and speaks MCP 2026-07-28 over stdio. The backend starts it and calls it through an MCP client for every query that needs market data.

Tools: `get_income_statements`, `get_balance_sheets`, `get_cash_flow_statements`, `get_current_stock_price`, `get_historical_stock_prices`, `get_company_news`, `get_available_crypto_tickers`, `get_crypto_prices`, `get_historical_crypto_prices`, `get_current_crypto_price`, `get_sec_filings`.

It needs a `FINANCIAL_DATASETS_API_KEY` from financialdatasets.ai. Replace `/path/to` below with where you cloned this repo.

Claude Code:

```sh
claude mcp add market-intel -e FINANCIAL_DATASETS_API_KEY=your_key -- uv --directory /path/to/Market_intelligence_MCP/mcp-server-main run server.py
```

Codex CLI:

```sh
codex mcp add market-intel --env FINANCIAL_DATASETS_API_KEY=your_key -- uv --directory /path/to/Market_intelligence_MCP/mcp-server-main run server.py
```

Gemini CLI (no `--` before the command):

```sh
gemini mcp add -s user -e FINANCIAL_DATASETS_API_KEY=your_key market-intel uv --directory /path/to/Market_intelligence_MCP/mcp-server-main run server.py
```

Claude Desktop (`claude_desktop_config.json`) and Cursor (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "market-intel": {
      "command": "uv",
      "args": ["--directory", "/path/to/Market_intelligence_MCP/mcp-server-main", "run", "server.py"],
      "env": { "FINANCIAL_DATASETS_API_KEY": "your_key" }
    }
  }
}
```

VS Code: copy `.vscode/mcp.json.example` to `.vscode/mcp.json`; it asks for the key on first start.

MCP Inspector:

```sh
npx @modelcontextprotocol/inspector uv --directory /path/to/Market_intelligence_MCP/mcp-server-main run server.py
```

Checked on 2026-10-08: Claude Code 2.1.294 connects and MCP Inspector lists all 11 tools and runs them; Codex CLI 0.156.1 accepts the config; Gemini CLI 0.63.0 accepts the config.

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export FINANCIAL_DATASETS_API_KEY=your_financial_api_key_here
```

Get your Gemini API key from: https://aistudio.google.com/apikey

### 3. Start the Server

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok"
}
```

### Non-Streaming Query

Request latest stock market news:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me the latest news on the stock market."}'
```

Request stock price:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is NVIDIA stock price?"}'
```

Request cryptocurrency price:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Bitcoin price right now?"}'
```

Response Format:
```json
{
  "session_id": "61933c11-6c76-4a0e-925f-bd0d16e51e34",
  "answer": "The NVIDIA Corporation (NVDA) stock price is $183.16 as of October 10, 2025..."
}
```

### Streaming Query

```bash
curl -N -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me the latest stock market news"}' \
  --no-buffer
```

Response Format (Server-Sent Events):
```
data: Analyzing...

data: Here's the latest stock market news...

event: done
data: ccb2dea9-fb94-4522-ac78-f835000fb7c5
```

### Context Preservation

First query:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Tesla stock price?"}'
```

Follow-up query using session_id from previous response:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What about their competitors?", "session_id": "SESSION_ID_FROM_PREVIOUS_RESPONSE"}'
```

## Architecture

### Two-Stage AI Pipeline

Stage 1: Ticker Extraction
- Gemini extracts ticker symbol and query type using JSON mode
- Determines if financial data is needed

Stage 2: Data Synthesis
- Calls MCP financial server for real-time data
- Enables Google Search grounding for latest context
- Combines all sources and sends to Gemini for synthesis

### Data Flow

```
User Query
    |
Stage 1: Extract Ticker (Gemini)
    |
Stage 2a: Fetch MCP Financial Data
    |
Stage 2b: Google Search Grounding
    |
Stage 2c: Gemini Synthesis
    |
Response with Citations
```

### Project Structure

```
Market_intelligence_MCP/
├── api/
│   └── main.py              - FastAPI application with endpoints
├── market_intel_service/
│   ├── config.py            - Configuration and API keys
│   ├── llm.py               - Gemini AI client with two-stage pipeline
│   ├── chat.py              - Query orchestration
│   └── memory.py            - SQLite conversation storage
├── mcp-server-main/
│   ├── server.py            - MCP financial data server
│   └── pyproject.toml       - MCP server dependencies
├── tests/
│   └── test_errors.py       - provider errors never reach the caller
├── README.md                - This file
├── requirements.txt         - Python dependencies
└── Dockerfile               - Docker configuration for deployment
```

## Tests

```bash
pip install pytest
pytest tests
```

The tests make the Gemini client fail with an error that quotes an API key and check that neither the full answer nor the streamed one passes it on. Running the server with a wrong key and calling both endpoints shows the same fixed message.
