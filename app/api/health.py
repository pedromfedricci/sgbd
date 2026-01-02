from app.api.dependencies import get_db_async_session

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["health"])


@router.get("/health", include_in_schema=False)
async def health(session: AsyncSession = get_db_async_session()):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
