from __future__ import annotations

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

from market_intel_service.chat import answer_query, answer_query_stream, ensure_initialized

app = FastAPI(title="Market Intelligence API", version="0.1.0")


class QueryRequest(BaseModel):
    message: str = Field(..., description="User question")
    session_id: Optional[str] = Field(None, description="Optional session ID for context continuity")
    model: Optional[str] = Field(None, description="Optional model override")
    context_window: Optional[int] = Field(None, description="Optional number of prior messages to include")


class QueryResponse(BaseModel):
    session_id: str
    answer: str


@app.on_event("startup")
async def _startup():
    await ensure_initialized()


@app.get("/")
async def root():
    return {
        "name": "Market Intelligence API",
        "version": "0.1.0",
        "description": "AI-powered market intelligence with MCP architecture",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "query_stream": "/query/stream",
            "docs": "/docs"
        },
        "features": [
            "Real-time stock prices and crypto data",
            "Financial statements and SEC filings",
            "Company news and market analysis",
            "Context-aware conversations",
            "Google Search grounding"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="'message' must be non-empty")
    result = await answer_query(
        message=req.message.strip(),
        session_id=req.session_id,
        model=req.model,
        context_window=req.context_window,
    )
    return result


@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    """
    Streaming endpoint for real-time chat experience.
    Returns Server-Sent Events (SSE) format.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="'message' must be non-empty")
    
    async def event_generator():
        """Generate SSE events for streaming response."""
        session_id = None
        try:
            async for chunk_data in answer_query_stream(
                message=req.message.strip(),
                session_id=req.session_id,
                model=req.model,
                context_window=req.context_window,
            ):
                # chunk_data is a dict with 'session_id' and 'chunk'
                if 'session_id' in chunk_data:
                    session_id = chunk_data['session_id']
                
                if 'chunk' in chunk_data:
                    # Send as SSE format
                    yield f"data: {chunk_data['chunk']}\n\n"
            
            # Send final event with session_id
            if session_id:
                yield f"event: done\ndata: {session_id}\n\n"
        except Exception:
            logging.getLogger(__name__).exception("stream failed")
            yield "event: error\ndata: The answer service is unavailable right now.\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

