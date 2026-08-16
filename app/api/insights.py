from fastapi import APIRouter

from app.api.deps import player_rows
from app.insights import insights_for
from app.schemas import Insight, View

router = APIRouter(prefix="/api", tags=["insights"])


@router.get("/insights")
def get_insights(batter_id: int, view: View = View.SWING) -> list[Insight]:
    return insights_for(player_rows(batter_id), view)
