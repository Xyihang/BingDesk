"""
塔罗牌 API 接口
"""
import json
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.tarot_reading import TarotReading

router = APIRouter(prefix="/tarot", tags=["tarot"])


class TarotReadingRequest(BaseModel):
    """塔罗牌占卜请求"""
    months: int = 1
    question: Optional[str] = None


class TarotResponse(BaseModel):
    """塔罗牌占卜响应"""
    success: bool
    data: Optional[dict] = None
    message: str = ""


async def _save_reading(
    db: AsyncSession,
    reading_type: str,
    cards: list,
    ai_interpretation: Optional[str] = None,
    question: Optional[str] = None,
    period_months: Optional[int] = None,
    overall_fortune: Optional[str] = None,
) -> TarotReading:
    reading = TarotReading(
        reading_type=reading_type,
        question=question,
        period_months=period_months,
        cards_json=json.dumps(cards, ensure_ascii=False),
        ai_interpretation=ai_interpretation,
        overall_fortune=overall_fortune,
    )
    db.add(reading)
    await db.flush()
    await db.refresh(reading)
    return reading


def _reading_to_dict(r: TarotReading) -> dict:
    return {
        "id": r.id,
        "reading_type": r.reading_type,
        "question": r.question,
        "period_months": r.period_months,
        "cards": json.loads(r.cards_json) if r.cards_json else [],
        "ai_interpretation": r.ai_interpretation,
        "overall_fortune": r.overall_fortune,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
    }


@router.post("/reading", response_model=TarotResponse)
async def get_tarot_reading(request: TarotReadingRequest, db: AsyncSession = Depends(get_db)):
    try:
        from app.services.tarot_service import TarotService

        if request.months < 1 or request.months > 12:
            raise HTTPException(status_code=400, detail="月数必须在 1-12 之间")

        tarot = TarotService()
        reading = await tarot.monthly_reading(
            months=request.months,
            question=request.question
        )

        monthly_cards = reading.get("monthly_readings", [])
        cards_for_save = [m["card"] for m in monthly_cards]

        saved = await _save_reading(
            db=db,
            reading_type="monthly",
            cards=cards_for_save,
            ai_interpretation=reading.get("ai_interpretation"),
            question=request.question,
            period_months=request.months,
            overall_fortune=reading.get("overall_fortune"),
        )

        reading["history_id"] = saved.id

        if request.question:
            reading["question"] = request.question

        return TarotResponse(
            success=True,
            data=reading,
            message=f"已完成{request.months}个月的塔罗牌占卜（含AI解读）"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily", response_model=TarotResponse)
async def get_daily_reading(db: AsyncSession = Depends(get_db)):
    try:
        from app.services.tarot_service import TarotService

        tarot = TarotService()
        reading = await tarot.daily_reading()

        card = reading.get("card", {})

        saved = await _save_reading(
            db=db,
            reading_type="daily",
            cards=[card],
            ai_interpretation=reading.get("ai_interpretation"),
        )

        reading["history_id"] = saved.id

        return TarotResponse(
            success=True,
            data=reading,
            message="每日塔罗牌已抽取（含AI解读）"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/celtic-cross", response_model=TarotResponse)
async def get_celtic_cross_reading(db: AsyncSession = Depends(get_db)):
    try:
        from app.services.tarot_service import TarotService

        tarot = TarotService()
        reading = await tarot.celtic_cross_reading()

        raw_cards = reading.get("cards", [])
        cards_for_save = [item["card"] for item in raw_cards if isinstance(item, dict) and "card" in item]

        saved = await _save_reading(
            db=db,
            reading_type="celtic",
            cards=cards_for_save,
            ai_interpretation=reading.get("ai_interpretation"),
        )

        reading["history_id"] = saved.id

        return TarotResponse(
            success=True,
            data=reading,
            message="凯尔特十字牌阵已完成（含AI解读）"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards", response_model=TarotResponse)
async def get_all_cards():
    try:
        from app.services.tarot_service import TarotService

        tarot = TarotService()
        all_cards = [card.to_dict() for card in tarot.deck]

        return TarotResponse(
            success=True,
            data={
                "total": len(all_cards),
                "major_arcana": [c for c in all_cards if c["is_major"]],
                "minor_arcana": [c for c in all_cards if not c["is_major"]]
            },
            message="已获取所有塔罗牌信息"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=TarotResponse)
async def get_reading_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    reading_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(TarotReading).order_by(desc(TarotReading.created_at))
        if reading_type:
            query = query.where(TarotReading.reading_type == reading_type)

        count_query = select(TarotReading)
        if reading_type:
            count_query = count_query.where(TarotReading.reading_type == reading_type)

        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        readings = result.scalars().all()

        return TarotResponse(
            success=True,
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [_reading_to_dict(r) for r in readings],
            },
            message="获取历史记录成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{reading_id}", response_model=TarotResponse)
async def get_reading_detail(reading_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(TarotReading).where(TarotReading.id == reading_id)
        )
        reading = result.scalar_one_or_none()

        if not reading:
            raise HTTPException(status_code=404, detail="记录不存在")

        return TarotResponse(
            success=True,
            data=_reading_to_dict(reading),
            message="获取详情成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{reading_id}", response_model=TarotResponse)
async def delete_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(TarotReading).where(TarotReading.id == reading_id)
        )
        reading = result.scalar_one_or_none()

        if not reading:
            raise HTTPException(status_code=404, detail="记录不存在")

        await db.delete(reading)
        await db.flush()

        return TarotResponse(
            success=True,
            message="删除成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
