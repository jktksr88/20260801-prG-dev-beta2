from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.database.session import get_db
from app.models import CropProfile

router=APIRouter(prefix="/plants",tags=["plants"])

def serialize(c:CropProfile,detail:bool=False):
    data={"id":c.id,"slug":c.slug,"scientific_name":c.species.scientific_name,"name_en":c.name_en,"name_id":c.name_id,"category":c.category,"annual_or_perennial":c.annual_or_perennial,"parameters":c.parameters,"verification_status":c.verification_status,"confidence_level":c.confidence_level}
    if detail:
        data.update({"alternative_names_en":c.alternative_names_en,"alternative_names_id":c.alternative_names_id,"edible_parts":c.edible_parts,"guidance_en":c.guidance_en,"guidance_id":c.guidance_id,"source_metadata":c.source_metadata,"fields_requiring_review":c.fields_requiring_review})
    return data

@router.get("")
def list_plants(category:str|None=None,q:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(50,ge=1,le=50),db:Session=Depends(get_db)):
    stmt=select(CropProfile).options(selectinload(CropProfile.species)).where(CropProfile.active.is_(True))
    count=select(func.count()).select_from(CropProfile).where(CropProfile.active.is_(True))
    if category: stmt=stmt.where(CropProfile.category==category); count=count.where(CropProfile.category==category)
    if q:
        term=f"%{q}%"; stmt=stmt.where((CropProfile.name_en.ilike(term))|(CropProfile.name_id.ilike(term))|(CropProfile.slug.ilike(term))); count=count.where((CropProfile.name_en.ilike(term))|(CropProfile.name_id.ilike(term))|(CropProfile.slug.ilike(term)))
    total=db.scalar(count) or 0
    items=db.scalars(stmt.order_by(CropProfile.category,CropProfile.name_en).offset((page-1)*page_size).limit(page_size)).all()
    return {"items":[serialize(x) for x in items],"page":page,"page_size":page_size,"total":total}

@router.get("/{slug}")
def plant_detail(slug:str,db:Session=Depends(get_db)):
    crop=db.scalar(select(CropProfile).options(selectinload(CropProfile.species)).where(CropProfile.slug==slug,CropProfile.active.is_(True)))
    if not crop: raise HTTPException(404,"Plant profile not found")
    return serialize(crop,True)
