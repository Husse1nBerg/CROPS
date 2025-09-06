# In server/app/services/data_processor.py
"""
Service for processing and cleaning scraped product data.
"""
import logging
import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Note: These are dependencies you will need to create
from app.models.product import Product
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.scrapers.base_scraper import ProductData
from app.utils.price_calculator import PriceCalculator

logger = logging.getLogger(__name__)

class DataProcessor:

    @staticmethod
    def process_scraped_data(db: Session, store_id: int, scraped_products: List[ProductData]):
        """
        Process a list of scraped products and update the database.
        """
        if not scraped_products:
            logger.info(f"No products scraped for store_id: {store_id}. Nothing to process.")
            return

        for scraped_product in scraped_products:
            # Normalize and clean data
            if not scraped_product.name or scraped_product.price <= 0:
                continue # Skip invalid products

            # Find a matching product in our database
            db_product = DataProcessor._find_matching_product(db, scraped_product.name)
            
            if not db_product:
                # If product doesn't exist, we can choose to create it or skip it.
                # For this tracker, we'll assume we only track pre-defined products.
                continue

            # Check for an existing price entry for this product-store combination
            current_price = db.query(Price).filter(
                Price.product_id == db_product.id,
                Price.store_id == store_id
            ).first()

            if current_price:
                # Update existing price
                current_price.price = scraped_product.price
                current_price.is_available = scraped_product.is_available
                current_price.scraped_at = scraped_product.scraped_at
                # Add other fields to update as necessary
            else:
                # Create a new price entry
                new_price = Price(
                    product_id=db_product.id,
                    store_id=store_id,
                    price=scraped_product.price,
                    is_available=scraped_product.is_available,
                    product_url=scraped_product.product_url,
                    scraped_at=scraped_product.scraped_at
                )
                db.add(new_price)

            # Always add to history for trend analysis
            history_entry = PriceHistory(
                product_id=db_product.id,
                store_id=store_id,
                price=scraped_product.price,
                is_available=scraped_product.is_available
            )
            db.add(history_entry)

        try:
            db.commit()
        except Exception as e:
            logger.error(f"Database commit failed during data processing for store {store_id}: {e}")
            db.rollback()

    @staticmethod
    def _find_matching_product(db: Session, scraped_name: str) -> Optional[Product]:
        """
        Finds a product in the DB that matches the scraped name using keywords.
        """
        # A simple keyword matching strategy
        products = db.query(Product).all()
        for product in products:
            # Assuming keywords are stored as a JSON string array in the model
            keywords = product.keywords.lower().split(',')
            for keyword in keywords:
                if keyword.strip() in scraped_name.lower():
                    return product
        return None