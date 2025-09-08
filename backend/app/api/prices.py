"""
Prices API endpoints
Path: backend/app/api/prices.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.store import Store
from app.schemas.price import PriceResponse, PriceCreate, PriceTrend
from app.api.auth import get_current_user
from app.tasks.scraping_tasks import trigger_scraping

router = APIRouter()

@router.get("/health")
def prices_health_check(db: Session = Depends(get_db)):
    """Health check for prices API - no auth required"""
    try:
        # Check basic database connectivity
        total_prices = db.query(Price).count()
        total_products = db.query(Product).count()
        total_stores = db.query(Store).count()
        
        return {
            "status": "healthy",
            "prices_count": total_prices,
            "products_count": total_products,
            "stores_count": total_stores,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "error"
        }

@router.get("/test", response_model=List[PriceResponse])
def get_prices_test_no_auth(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    category: Optional[str] = None,
    is_available: Optional[bool] = None
):
    """Get current prices with filters"""
    try:
        # First check if we have any data at all
        total_prices = db.query(Price).count()
        if total_prices == 0:
            return []  # Return empty list if no prices exist
        
        # Build base query with proper error handling for joins
        query = db.query(Price)
        
        # Only add joins if we have related data
        try:
            query = query.join(Product, Price.product_id == Product.id)
            query = query.join(Store, Price.store_id == Store.id)
        except Exception as join_error:
            raise HTTPException(
                status_code=500,
                detail=f"Database join error: {str(join_error)}"
            )
        
        # Apply filters
        if product_id:
            query = query.filter(Price.product_id == product_id)
        if store_id:
            query = query.filter(Price.store_id == store_id)
        if category:
            query = query.filter(Product.category == category)
        if is_available is not None:
            query = query.filter(Price.is_available == is_available)
        
        # For empty database, return empty result without complex subquery
        if total_prices > 0:
            # Get latest prices only (most recent for each product-store combination)
            try:
                subquery = db.query(
                    Price.product_id,
                    Price.store_id,
                    db.func.max(Price.scraped_at).label('max_scraped_at')
                ).group_by(Price.product_id, Price.store_id).subquery()
                
                query = query.join(
                    subquery,
                    db.and_(
                        Price.product_id == subquery.c.product_id,
                        Price.store_id == subquery.c.store_id,
                        Price.scraped_at == subquery.c.max_scraped_at
                    )
                )
            except Exception as subquery_error:
                # If subquery fails, just get all prices without grouping
                pass
        
        # Execute query with proper error handling
        try:
            prices = query.offset(skip).limit(limit).all()
        except Exception as query_error:
            raise HTTPException(
                status_code=500,
                detail=f"Database query error: {str(query_error)}"
            )
        
        # Format response with error handling
        results = []
        for price in prices:
            try:
                # Calculate price change with error handling
                price_change = 0
                price_change_percent = 0
                try:
                    yesterday = datetime.utcnow() - timedelta(days=1)
                    previous_price = db.query(PriceHistory).filter(
                        PriceHistory.product_id == price.product_id,
                        PriceHistory.store_id == price.store_id,
                        PriceHistory.recorded_at < yesterday
                    ).order_by(PriceHistory.recorded_at.desc()).first()
                    
                    if previous_price:
                        price_change = price.price - previous_price.price
                        if previous_price.price > 0:
                            price_change_percent = (price_change / previous_price.price) * 100
                except Exception:
                    # If price history calculation fails, just use default values
                    pass
                
                results.append({
                    "id": price.id,
                    "product_id": price.product_id,
                    "product_name": getattr(price.product, 'name', 'Unknown Product'),
                    "store_id": price.store_id,
                    "store_name": getattr(price.store, 'name', 'Unknown Store'),
                    "price": price.price,
                    "original_price": price.original_price,
                    "price_per_kg": price.price_per_kg,
                    "pack_size": price.pack_size,
                    "pack_unit": price.pack_unit,
                    "is_available": price.is_available,
                    "is_discounted": price.is_discounted,
                    "price_change": price_change,
                    "price_change_percent": price_change_percent,
                    "product_url": price.product_url,
                    "image_url": price.image_url,
                    "scraped_at": price.scraped_at,
                    "created_at": price.created_at,
                    "updated_at": price.updated_at
                })
            except Exception as format_error:
                # Skip malformed entries but continue processing others
                continue
        
        return results
    
    except HTTPException:
        # Re-raise HTTP exceptions as they already have proper error messages
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[PriceResponse])
def get_prices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    category: Optional[str] = None,
    is_available: Optional[bool] = None
):
    """Get current prices with filters - requires authentication"""
    return get_prices_test_no_auth(db, skip, limit, product_id, store_id, category, is_available)

@router.post("/refresh")
async def refresh_prices(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Trigger price refresh (scraping)"""
    # Add scraping task to background
    background_tasks.add_task(trigger_scraping, db)
    
    # Update store statuses
    stores = db.query(Store).filter(Store.is_active == True).all()
    for store in stores:
        store.status = "scraping"
    db.commit()
    
    return {"message": "Price refresh initiated", "stores_count": len(stores)}

@router.get("/trends", response_model=List[PriceTrend])
def get_price_trends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    product_id: int = Query(...),
    store_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=30)
):
    """Get price trends for a product"""
    since = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.recorded_at >= since
    )
    
    if store_id:
        query = query.filter(PriceHistory.store_id == store_id)
    
    history = query.order_by(PriceHistory.recorded_at).all()
    
    # Group by date and store
    trends = {}
    for record in history:
        date_key = record.recorded_at.date().isoformat()
        store_key = record.store_id
        
        if date_key not in trends:
            trends[date_key] = {}
        
        trends[date_key][store_key] = {
            "price": record.price,
            "price_per_kg": record.price_per_kg,
            "is_available": record.is_available
        }
    
    return trends

@router.get("/{price_id}", response_model=PriceResponse)
def get_price(
    price_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific price by ID"""
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    return price