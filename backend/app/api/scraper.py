"""
Scraper API endpoints - Updated for real-time grocery store scraping
Path: backend/app/api/scraper.py
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import asyncio

from app.database import get_db
from app.models.store import Store
from app.api.auth import get_current_user
from app.tasks.scraping_tasks import scrape_store_task, scrape_all_stores_task, search_specific_product_task
from app.scrapers.scraper_manager import scraper_manager

router = APIRouter()

@router.post("/trigger")
async def trigger_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    store_id: Optional[int] = None
):
    """Trigger scraping for all stores or specific store"""
    if store_id:
        # Scrape specific store
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        if not store.is_active:
            raise HTTPException(status_code=400, detail="Store is not active")
        
        # Update status
        store.status = "scraping"
        db.commit()
        
        # Add to background tasks
        background_tasks.add_task(scrape_store_task, store_id)
        
        return {
            "message": f"Scraping initiated for {store.name}",
            "store_id": store_id
        }
    else:
        # Scrape all active stores
        stores = db.query(Store).filter(Store.is_active == True).all()
        
        if not stores:
            raise HTTPException(status_code=404, detail="No active stores found")
        
        # Update all statuses
        for store in stores:
            store.status = "scraping"
        db.commit()
        
        # Add to background tasks
        background_tasks.add_task(scrape_all_stores_task)
        
        return {
            "message": "Scraping initiated for all stores",
            "stores_count": len(stores)
        }

@router.get("/status")
def get_scraping_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current scraping status for all stores"""
    stores = db.query(Store).all()
    
    status = {
        "total_stores": len(stores),
        "active_stores": len([s for s in stores if s.is_active]),
        "scraping": len([s for s in stores if s.status == "scraping"]),
        "online": len([s for s in stores if s.status == "online"]),
        "offline": len([s for s in stores if s.status == "offline"]),
        "idle": len([s for s in stores if s.status == "idle"]),
        "stores": [
            {
                "id": store.id,
                "name": store.name,
                "status": store.status,
                "last_scraped": store.last_scraped,
                "is_active": store.is_active
            }
            for store in stores
        ]
    }
    
    return status

@router.post("/stop")
def stop_scraping(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Stop all ongoing scraping tasks"""
    stores = db.query(Store).filter(Store.status == "scraping").all()
    
    for store in stores:
        store.status = "idle"
    
    db.commit()
    
    return {
        "message": "Scraping stopped",
        "affected_stores": len(stores)
    }

@router.post("/search/{product_name}")
def search_product_across_stores(
    product_name: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Search for a specific product across all active stores"""
    # Trigger background search task
    background_tasks.add_task(search_specific_product_task.delay, product_name)
    
    return {
        "message": f"Product search initiated for '{product_name}'",
        "product": product_name
    }

@router.get("/target-products")
def get_target_products(current_user = Depends(get_current_user)):
    """Get the list of target products being tracked"""
    target_products = scraper_manager.get_target_products()
    
    category_a = [p for p in target_products if p["category"] == "A"]
    category_b = [p for p in target_products if p["category"] == "B"]
    
    return {
        "total_products": len(target_products),
        "category_a": category_a,
        "category_b": category_b,
        "summary": {
            "category_a_count": len(category_a),
            "category_b_count": len(category_b)
        }
    }

@router.post("/test-scraper/{store_id}")
async def test_single_scraper(
    store_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Test scraping for a single store (immediate response, not background task)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if not store.is_active:
        raise HTTPException(status_code=400, detail="Store is not active")
    
    try:
        # Run scraping immediately (not as background task)
        products = await scraper_manager.scrape_single_store(store_id)
        
        return {
            "store_id": store_id,
            "store_name": store.name,
            "products_found": len(products),
            "sample_products": [
                {
                    "name": p.name,
                    "price": float(p.price),
                    "price_per_kg": float(p.price_per_kg) if p.price_per_kg else None,
                    "is_available": p.is_available,
                    "is_organic": p.is_organic
                }
                for p in products[:5]  # Show first 5 products
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")

@router.get("/stores-summary")
def get_stores_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get summary of all stores and their scraping status"""
    stores = db.query(Store).all()
    
    return {
        "total_stores": len(stores),
        "active_stores": len([s for s in stores if s.is_active]),
        "scraping_now": len([s for s in stores if s.status == "scraping"]),
        "stores": [
            {
                "id": store.id,
                "name": store.name,
                "url": store.url,
                "status": store.status,
                "is_active": store.is_active,
                "last_scraped": store.last_scraped,
                "scraper_module": store.scraper_module
            }
            for store in stores
        ]
    }