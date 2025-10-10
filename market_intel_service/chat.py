from __future__ import annotations

import uuid
from typing import AsyncIterator, Dict, Optional

from .config import settings
from .llm import make_llm
from .memory import append_messages, fetch_context, init_db


async def ensure_initialized() -> None:
    init_db()


async def answer_query(
    message: str,
    session_id: Optional[str] = None,
    model: Optional[str] = None,
    context_window: Optional[int] = None,
) -> Dict[str, str]:
    """Answer a market-related question with preserved context."""
    await ensure_initialized()
    sid = session_id or str(uuid.uuid4())
    ctx_n = context_window or settings.context_window

    # Context messages
    context = fetch_context(sid, limit=ctx_n)
    messages = [{"role": r, "content": c} for r, c in context]
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": settings.system_prompt})
    messages.append({"role": "user", "content": message})

    # Persist user message before generation
    append_messages(sid, [("user", message)])

    llm = make_llm()
    text = await llm.generate(messages, model=model)

    # Persist assistant reply
    append_messages(sid, [("assistant", text)])

    return {"session_id": sid, "answer": text}


async def answer_query_stream(
    message: str,
    session_id: Optional[str] = None,
    model: Optional[str] = None,
    context_window: Optional[int] = None,
) -> AsyncIterator[Dict[str, str]]:
    """Stream answer to a market-related question with preserved context."""
    await ensure_initialized()
    sid = session_id or str(uuid.uuid4())
    ctx_n = context_window or settings.context_window

    # Build context messages
    context = fetch_context(sid, limit=ctx_n)
    messages = [{"role": r, "content": c} for r, c in context]
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": settings.system_prompt})
    messages.append({"role": "user", "content": message})

    # Persist user message before generation
    append_messages(sid, [("user", message)])
    yield {"session_id": sid}

    # Generation with configured LLM and stream
    llm = make_llm()
    full_response = []
    
    async for chunk in llm.generate_stream(messages, model=model):
        full_response.append(chunk)
        yield {"chunk": chunk}
    complete_text = "".join(full_response)
    append_messages(sid, [("assistant", complete_text)])

