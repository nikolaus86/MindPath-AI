from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import RouteResponse
from ..services.router_service import APP_TITLES, RouterService
from ..services.session_service import SessionService

router = APIRouter(prefix="/router", tags=["router"])


@router.post("/{session_id}/route", response_model=RouteResponse)
async def route_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RouteResponse:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    app_id, reason, context = await RouterService.route_session(db, session)
    return RouteResponse(
        recommended_app=app_id,
        title=APP_TITLES[app_id],
        reason=reason,
        context=context,
    )
