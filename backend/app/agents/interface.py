"""Stable API surface of the agent system.

Routers (and any future caller) import ONLY from this module — the
individual agents behind it can be refactored freely.
"""

from __future__ import annotations

import uuid
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import business_brain, memory_manager, outreach_writer, supervisor
from app.db.models import BrainBriefing, OutreachDraft


async def run_brain_ask(
    org_id: uuid.UUID, question: str, db: AsyncSession
) -> AsyncIterator[str]:
    """Stream a Business Brain answer grounded in the org's context + signals."""
    async for chunk in business_brain.ask(org_id, question, db):
        yield chunk


async def generate_outreach(
    account_id: uuid.UUID, db: AsyncSession
) -> list[OutreachDraft]:
    """Generate and persist 3 outreach variants for an account."""
    return await outreach_writer.generate_outreach_for_account(account_id, db)


async def generate_briefing(org_id: uuid.UUID, db: AsyncSession) -> BrainBriefing:
    """Generate (or fetch today's) daily briefing for an organization."""
    return await business_brain.generate_briefing(org_id, db)


async def coach_deal(entry_id: uuid.UUID, db: AsyncSession) -> str:
    """Deal coaching for one Action Queue entry."""
    return await business_brain.coach(entry_id, db)


async def run_pipeline(org_id: uuid.UUID, db: AsyncSession) -> dict:
    """One full supervisor cycle: scout -> classify -> score -> queue."""
    return await supervisor.run_pipeline(org_id, db)


async def record_outreach_outcome(
    draft_id: uuid.UUID, outcome: str, db: AsyncSession
):
    """Record an outreach outcome and update the org's signal-weight memory."""
    return await memory_manager.record_outcome(draft_id, outcome, db)
