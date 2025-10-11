# Market Intelligence AI Backend Service

AI-powered market intelligence backend service with real-time financial data integration and web search capabilities.

## Live API Deployment

The API is deployed and accessible at:

**Base URL:** https://akv2011-market-intel-api.hf.space

**API Documentation:** https://akv2011-market-intel-api.hf.space/docs

**Endpoints:**
- GET /health - Health check endpoint
- POST /query - Non-streaming JSON responses
- POST /query/stream - Server-Sent Events streaming for real-time responses

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
  - POST /query - Non-streaming JSON responses (REQUIRED)
  - POST /query/stream - Server-Sent Events streaming for real-time chat (BONUS)
  - GET /health - Health check endpoint
- Context Memory: SQLite-based conversation history with session management
- Google Gemini AI: Latest gemini-2.0-flash-001 model with Google Search grounding
- Two-Stage Intelligence:
  - Stage 1: Extract ticker symbols and query type
  - Stage 2: Fetch MCP financial data + Google Search + AI synthesis

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

### Using the Deployed API

#### Health Check

```bash
curl https://akv2011-market-intel-api.hf.space/health
```

Response:
```json
{
  "status": "ok"
}
```

#### Non-Streaming Query

Request latest stock market news:
```bash
curl -X POST https://akv2011-market-intel-api.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me the latest news on the stock market."}'
```

Request stock price:
```bash
curl -X POST https://akv2011-market-intel-api.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is NVIDIA stock price?"}'
```

Request cryptocurrency price:
```bash
curl -X POST https://akv2011-market-intel-api.hf.space/query \
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

#### Streaming Query

```bash
curl -N -X POST https://akv2011-market-intel-api.hf.space/query/stream \
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

#### Context Preservation

First query:
```bash
curl -X POST https://akv2011-market-intel-api.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Tesla stock price?"}'
```

Follow-up query using session_id from previous response:
```bash
curl -X POST https://akv2011-market-intel-api.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What about their competitors?", "session_id": "SESSION_ID_FROM_PREVIOUS_RESPONSE"}'
```

### Testing Locally

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Non-Streaming Endpoint

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is NVIDIA stock price?"}'
```

#### Streaming Endpoint

```bash
curl -N -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Bitcoin price right now?"}' \
  --no-buffer
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
├── docs/
│   └── DEPLOYMENT.md        - Detailed deployment guide
├── README.md                - This file
├── requirements.txt         - Python dependencies
├── Dockerfile               - Docker configuration for deployment
└── vercel.json              - Vercel deployment configuration
```

## Requirements

- fastapi==0.115.2
- uvicorn==0.30.6
- google-genai==1.42.0
- pydantic==2.9.2
- httpx==0.28.1
- python-multipart


