"""Signal routes: real-time SSE stream, manual signals, history."""

from __future__ import annotations

import asyncio
import json
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Account, Organization, Signal, utcnow
from app.db.session import get_db, get_session_factory
from app.routers.deps import get_current_org

router = APIRouter(prefix="/signals", tags=["signals"])

STREAM_POLL_SECONDS = 3.0
STREAM_HEARTBEAT_EVERY = 5  # polls between heartbeats


def _serialize(signal: Signal, company_name: str = "") -> dict:
    return {
        "id": str(signal.id),
        "account_id": str(signal.account_id),
        "company_name": company_name,
        "signal_type": signal.signal_type,
        "source": signal.source,
        "title": signal.title,
        "summary": signal.summary,
        "urgency_tier": signal.urgency_tier,
        "budget_implication": signal.budget_implication,
        "detected_at": signal.detected_at.isoformat() if signal.detected_at else None,
        "status": signal.status,
    }


@router.get("/stream")
async def stream_signals(
    org: Organization = Depends(get_current_org),
) -> StreamingResponse:
    """Server-sent events: pushes signals newer than the connection start.

    Polls the database every ``STREAM_POLL_SECONDS`` and emits heartbeat
    comments so proxies keep the connection alive.
    """
    org_id = org.id

    async def event_stream():
        cursor = utcnow()
        polls = 0
        factory = get_session_factory()
        while True:
            try:
                async with factory() as session:
                    result = await session.execute(
                        select(Signal, Account.company_name)
                        .join(Account, Signal.account_id == Account.id)
                        .where(Account.org_id == org_id, Signal.detected_at > cursor)
                        .order_by(Signal.detected_at.asc())
                    )
                    rows = result.all()
                for signal, company_name in rows:
                    cursor = max(cursor, signal.detected_at)
                    payload = json.dumps(_serialize(signal, company_name))
                    yield f"data: {payload}\n\n".encode("utf-8")
                polls += 1
                if polls % STREAM_HEARTBEAT_EVERY == 0:
                    yield b": heartbeat\n\n"
                await asyncio.sleep(STREAM_POLL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as exc:  # noqa: BLE001 — keep the stream alive
                yield f": error {exc}\n\n".encode("utf-8")
                await asyncio.sleep(STREAM_POLL_SECONDS)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class CustomSignalRequest(BaseModel):
    account_id: Optional[str] = None
    company_name: str = Field(default="", max_length=255)
    signal_type: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=512)
    raw_data: dict = Field(default_factory=dict)


@router.post("/custom")
async def add_custom_signal(
    payload: CustomSignalRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Manually add a signal, attaching to an existing or new account."""
    account = None
    if payload.account_id:
        account = (
            await db.execute(
                select(Account).where(
                    Account.id == payload.account_id, Account.org_id == org.id
                )
            )
        ).scalars().first()
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found.")
    elif payload.company_name.strip():
        name = payload.company_name.strip()
        account = (
            await db.execute(
                select(Account).where(
                    Account.org_id == org.id, Account.company_name == name
                )
            )
        ).scalars().first()
        if account is None:
            account = Account(org_id=org.id, company_name=name)
            db.add(account)
            await db.flush()
    else:
        raise HTTPException(
            status_code=422, detail="Provide account_id or company_name."
        )

    signal = Signal(
        account_id=account.id,
        signal_type=payload.signal_type,
        source="manual",
        title=payload.title,
        raw_data=payload.raw_data,
        status="new",
    )
    db.add(signal)
    await db.commit()
    return {"id": str(signal.id), "account_id": str(account.id), "status": "created"}


@router.get("/history/{days}")
async def signal_history(
    days: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """All signals detected in the last N days (1-365), newest first."""
    if not 1 <= days <= 365:
        raise HTTPException(status_code=422, detail="days must be between 1 and 365.")
    since = utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Signal, Account.company_name)
        .join(Account, Signal.account_id == Account.id)
        .where(Account.org_id == org.id, Signal.detected_at >= since)
        .order_by(Signal.detected_at.desc())
    )
    rows = result.all()
    return {
        "days": days,
        "count": len(rows),
        "signals": [_serialize(signal, name) for signal, name in rows],
    }
