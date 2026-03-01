"""
Companies API routes — track/untrack/list companies.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.db import crud, schemas

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("")
def list_companies(db: Session = Depends(get_db)):
    companies = crud.get_tracked_companies(db)
    return [
        {
            "id": c.id, "name": c.name, "domain": c.domain,
            "notify": c.notify, "last_checked": c.last_checked,
            "created_at": c.created_at,
            "logo_url": f"https://logo.clearbit.com/{c.domain}" if c.domain else "",
        }
        for c in companies
    ]


@router.post("/track")
def track_company(req: schemas.CompanyTrackRequest, db: Session = Depends(get_db)):
    company = crud.track_company(db, req.name, req.domain, req.notify)
    return {"id": company.id, "name": company.name, "message": "Company tracked"}


@router.delete("/{company_id}/track")
def untrack_company(company_id: int, db: Session = Depends(get_db)):
    if not crud.untrack_company(db, company_id):
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company untracked"}


@router.patch("/{company_id}")
def update_company(company_id: int, req: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    c = crud.update_company(db, company_id, req.model_dump(exclude_none=True))
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"id": c.id, "name": c.name, "notify": c.notify}
