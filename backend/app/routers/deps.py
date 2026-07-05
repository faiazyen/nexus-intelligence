"""Shared FastAPI dependencies.

MVP auth: the ``X-Org-Id`` header carries the organization UUID. Clerk (or
any real IdP) slots in behind ``get_current_org`` without touching routers.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Organization
from app.db.session import get_db

DEMO_ORG_NAME = "NEXUS Demo Org"


async def get_current_org(
    x_org_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """Resolve the calling organization from the ``X-Org-Id`` header.

    Falls back to the seeded demo org when the header is absent (so the demo
    frontend works with zero auth setup); raises 401 when a header is present
    but invalid, and 404 when the org does not exist.
    """
    if x_org_id is None:
        result = await db.execute(
            select(Organization).where(Organization.name == DEMO_ORG_NAME)
        )
        org = result.scalars().first()
        if org is None:
            raise HTTPException(
                status_code=401,
                detail="No X-Org-Id header and no demo org seeded. "
                "Run `python -m app.db.seed` or send X-Org-Id.",
            )
        return org

    try:
        org_uuid = uuid.UUID(x_org_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-Org-Id is not a valid UUID.")

    result = await db.execute(select(Organization).where(Organization.id == org_uuid))
    org = result.scalars().first()
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return org
