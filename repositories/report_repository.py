from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.domain.reports import Report
from models.schemas.reports import ReportCreate, ReportResponse


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report_data: dict) -> Report:
        try:
            report = Report(**report_data)
            self.session.add(report)
            await self.session.commit()
            await self.session.refresh(report)
            return report
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Не удалось создать отчет")

    async def get_by_id(self, report_id: int) -> Report | None:
        result = await self.session.execute(
            select(Report)
            .options(
                selectinload(Report.project),
            )
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_reports_by_project(self, project_id: int, limit: int = 50) -> list[Report]:
        result = await self.session.execute(
            select(Report)
            .options(
                selectinload(Report.project),
            )
            .where(Report.project_id == project_id)
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def update(self, report_id: int, update_data: dict) -> Report:
        try:
            report = await self.get_by_id(report_id)
            if not report:
                raise HTTPException(status_code=404, detail="Отчет не найден")

            for key, value in update_data.items():
                setattr(report, key, value)

            await self.session.commit()
            await self.session.refresh(report)
            return report
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Не удалось обновить отчет")

    async def delete(self, report_id: int) -> bool:
        try:
            report = await self.get_by_id(report_id)
            if not report:
                raise HTTPException(status_code=404, detail="Отчет не найден")

            await self.session.delete(report)
            await self.session.commit()
            return True
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Не удалось удалить отчет")