# In server/app/services/price_service.py
"""
Price service for managing price data
Path: backend/app/services/price_service.py
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

# Note: These are dependencies you will need to create
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.store import Store

class PriceService:
    """Service for managing price data and analytics"""
    
    @staticmethod
    def get_current_prices(
        db: Session,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Get current prices with filters."""
        query = db.query(Price).join(Product).join(Store)
        
        if product_id:
            query = query.filter(Price.product_id == product_id)
        if store_id:
            query = query.filter(Price.store_id == store_id)
        
        # Subquery to get the latest scrape for each product-store pair
        subquery = db.query(
            Price.product_id,
            Price.store_id,
            func.max(Price.scraped_at).label('max_scraped_at')
        ).group_by(Price.product_id, Price.store_id).subquery()
        
        query = query.join(
            subquery,
            and_(
                Price.product_id == subquery.c.product_id,
                Price.store_id == subquery.c.store_id,
                Price.scraped_at == subquery.c.max_scraped_at
            )
        )
        
        prices = query.offset(skip).limit(limit).all()
        
        # Format results with price change calculation
        results = []
        for price in prices:
            price_data = PriceService._format_price_with_change(db, price)
            results.append(price_data)
        
        return results
    
    @staticmethod
    def _format_price_with_change(db: Session, price: Price) -> Dict:
        """Helper to format a single price object with its change percentage."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        previous_price_obj = db.query(PriceHistory).filter(
            PriceHistory.product_id == price.product_id,
            PriceHistory.store_id == price.store_id,
            PriceHistory.recorded_at < yesterday
        ).order_by(PriceHistory.recorded_at.desc()).first()
        
        price_change_percent = 0
        if previous_price_obj and previous_price_obj.price > 0:
            price_change = price.price - previous_price_obj.price
            price_change_percent = (price_change / previous_price_obj.price) * 100
        
        return {
            "id": price.id,
            "product_id": price.product_id,
            "product_name": price.product.name,
            "store_id": price.store_id,
            "store_name": price.store.name,
            "price": price.price,
            "original_price": price.original_price,
            "price_per_kg": price.price_per_kg,
            "is_available": price.is_available,
            "product_url": price.product_url,
            "price_change_percent": round(price_change_percent, 2),
            "scraped_at": price.scraped_at
        }
        
    @staticmethod
    def get_price_trends(db: Session, product_id: int, days: int) -> List[Dict]:
        """Get price history for a product for trend analysis."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        history = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= since_date
        ).order_by(PriceHistory.recorded_at.asc()).all()
        
        return [
            {"date": record.recorded_at.strftime("%Y-%m-%d"), "price": record.price}
            for record in history
        ]