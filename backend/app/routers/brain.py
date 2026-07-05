"""NEXUS BRAIN routes: onboarding, briefings, streaming Q&A, deal coaching."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BusinessContextDoc, Organization
from app.db.session import get_db
from app.routers.deps import get_current_org

router = APIRouter(prefix="/brain", tags=["brain"])


class ContextDocIn(BaseModel):
    doc_type: str = Field(default="general", max_length=64)
    title: str = Field(default="", max_length=255)
    content: str = Field(min_length=1)


class OnboardRequest(BaseModel):
    documents: list[ContextDocIn] = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


@router.post("/onboard")
async def onboard(
    payload: OnboardRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Ingest business context documents (proposals, case studies, pricing...)."""
    created = []
    for doc in payload.documents:
        row = BusinessContextDoc(
            org_id=org.id,
            doc_type=doc.doc_type,
            title=doc.title or doc.content[:60],
            content=doc.content,
        )
        db.add(row)
        created.append(row)
    await db.commit()
    return {"ingested": len(created), "ids": [str(row.id) for row in created]}


@router.get("/briefing")
async def briefing(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Today's daily briefing; generated on first request of the day."""
    try:
        from app.agents.interface import generate_briefing
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"Agent system unavailable: {exc}")
    row = await generate_briefing(org.id, db)
    return {
        "id": str(row.id),
        "briefing_date": row.briefing_date.isoformat(),
        "content_markdown": row.content_markdown,
    }


@router.post("/ask")
async def ask(
    payload: AskRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Streaming chat with the Business Brain (SSE-style text stream)."""
    try:
        from app.agents.interface import run_brain_ask
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"Agent system unavailable: {exc}")

    async def event_stream():
        try:
            async for chunk in run_brain_ask(org.id, payload.question, db):
                yield f"data: {chunk}\n\n".encode("utf-8")
            yield b"data: [DONE]\n\n"
        except Exception as exc:  # noqa: BLE001 — surface inside the stream
            yield f"data: [ERROR] {exc}\n\n".encode("utf-8")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/deal/{entry_id}/coach")
async def deal_coach(
    entry_id: uuid.UUID,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Tactical coaching for one open opportunity in the Action Queue."""
    try:
        from app.agents.interface import coach_deal
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"Agent system unavailable: {exc}")
    try:
        advice = await coach_deal(entry_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"entry_id": str(entry_id), "coaching": advice}
