from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2 import functions as gf
from typing import List, Optional
from ..database import get_db, Merchant, Category, MerchantPhoto, Ambassador
from ..schemas import (
    Merchant as MerchantSchema, 
    MerchantCreate, 
    MerchantUpdate, 
    SearchRequest, 
    SearchResponse
)
from ..auth import get_current_user
from ..search_engine import ConversationalSearchEngine
import json

router = APIRouter(prefix="/merchants", tags=["merchants"])
search_engine = ConversationalSearchEngine()

@router.get("/", response_model=List[MerchantSchema])
async def get_merchants(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    is_open: Optional[bool] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = Query(5000, ge=100, le=50000),
    db: Session = Depends(get_db)
):
    """Get merchants with optional filters"""
    query = db.query(Merchant)
    
    # Apply filters
    if category_id:
        query = query.filter(Merchant.category_id == category_id)
    
    if is_open is not None:
        query = query.filter(Merchant.is_open == is_open)
    
    # Apply location filter
    if latitude and longitude:
        query = query.filter(
            func.ST_DWithin(
                Merchant.location,
                func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326),
                radius
            )
        )
    
    merchants = query.offset(skip).limit(limit).all()
    
    # Add distance calculation if location provided
    if latitude and longitude:
        for merchant in merchants:
            distance_query = db.execute(
                text("""
                SELECT ST_Distance(
                    location, 
                    ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
                ) as distance
                FROM merchants WHERE id = :merchant_id
                """),
                {"longitude": longitude, "latitude": latitude, "merchant_id": merchant.id}
            ).first()
            if distance_query:
                merchant.distance = distance_query.distance
    
    return merchants

@router.get("/{merchant_id}", response_model=MerchantSchema)
async def get_merchant(merchant_id: int, db: Session = Depends(get_db)):
    """Get a specific merchant by ID"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    return merchant

@router.post("/", response_model=MerchantSchema)
async def create_merchant(
    merchant_data: MerchantCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new merchant (ambassadors only)"""
    # Check if user is an ambassador
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ambassadors can create merchants"
        )
    
    # Create merchant
    merchant = Merchant(
        name=merchant_data.name,
        description=merchant_data.description,
        category_id=merchant_data.category_id,
        address=merchant_data.address,
        phone_number=merchant_data.phone_number,
        whatsapp_number=merchant_data.whatsapp_number,
        opening_hours=merchant_data.opening_hours,
        price_level=merchant_data.price_level,
        ambassador_id=ambassador.id,
        location=func.ST_SetSRID(
            func.ST_MakePoint(merchant_data.longitude, merchant_data.latitude), 
            4326
        )
    )
    
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    
    return merchant

@router.put("/{merchant_id}", response_model=MerchantSchema)
async def update_merchant(
    merchant_id: int,
    merchant_update: MerchantUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a merchant (ambassadors only)"""
    # Check if user is an ambassador
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ambassadors can update merchants"
        )
    
    # Get merchant
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    # Check if ambassador owns this merchant
    if merchant.ambassador_id != ambassador.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own merchants"
        )
    
    # Update merchant
    update_data = merchant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(merchant, field, value)
    
    db.commit()
    db.refresh(merchant)
    
    return merchant

@router.post("/{merchant_id}/photos")
async def upload_merchant_photo(
    merchant_id: int,
    image_url: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a photo for a merchant (ambassadors only)"""
    # Check if user is an ambassador
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ambassadors can upload photos"
        )
    
    # Get merchant
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    # Check if ambassador owns this merchant
    if merchant.ambassador_id != ambassador.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload photos for your own merchants"
        )
    
    # Create photo record
    photo = MerchantPhoto(
        merchant_id=merchant_id,
        image_url=image_url
    )
    
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    return {"message": "Photo uploaded successfully", "photo_id": photo.id}

@router.get("/{merchant_id}/status")
async def get_merchant_status(merchant_id: int, db: Session = Depends(get_db)):
    """Get current status of a merchant"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    return {
        "merchant_id": merchant_id,
        "is_open": merchant.is_open,
        "last_updated": merchant.updated_at,
        "opening_hours": merchant.opening_hours
    }

@router.post("/search", response_model=SearchResponse)
async def search_merchants(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search merchants using conversational search"""
    result = search_engine.search(db, search_request)
    
    return SearchResponse(
        merchants=result["merchants"],
        total_count=result["total_count"],
        query_processed=result["query_processed"],
        search_time_ms=result["search_time_ms"]
    )