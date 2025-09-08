"""
Centralized Scraper Manager
Coordinates scraping across all 9 target grocery stores
Path: backend/app/scrapers/scraper_manager.py
"""

import asyncio
import logging
from typing import List, Dict, Optional, Type
from datetime import datetime
from sqlalchemy.orm import Session

from app.scrapers.base_scraper import BaseScraper, ProductData
from app.scrapers.gourmet_scraper import GourmetScraper
from app.scrapers.rdna_scraper import RDNAScraper
from app.scrapers.metro_scraper import MetroScraper
from app.scrapers.spinneys_scraper import SpinneysScraper
from app.scrapers.rabbit_scraper import RabbitScraper
from app.scrapers.talabat_scraper import TalabatScraper
from app.scrapers.instashop_scraper import InstashopScraper
from app.scrapers.breadfast_scraper import BreadfastScraper

from app.database import get_db, SessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.price import Price

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages all store scrapers and coordinates data collection"""
    
    def __init__(self):
        self.scrapers: Dict[str, Type[BaseScraper]] = {
            "gourmet_scraper": GourmetScraper,
            "rdna_scraper": RDNAScraper,
            "metro_scraper": MetroScraper,
            "spinneys_scraper": SpinneysScraper,
            "rabbit_scraper": RabbitScraper,
            "talabat_scraper": TalabatScraper,
            "instashop_scraper": InstashopScraper,
            "breadfast_scraper": BreadfastScraper
        }
        
    async def scrape_all_stores(self) -> Dict[str, List[ProductData]]:
        """Scrape all active stores concurrently"""
        logger.info("Starting scraping across all stores...")
        
        db = SessionLocal()
        try:
            # Get all active stores
            active_stores = db.query(Store).filter(Store.is_active == True).all()
            
            if not active_stores:
                logger.warning("No active stores found")
                return {}
            
            # Create scraping tasks
            tasks = []
            store_names = []
            
            for store in active_stores:
                if store.scraper_module and store.scraper_module in self.scrapers:
                    scraper_class = self.scrapers[store.scraper_module]
                    task = asyncio.create_task(
                        self._scrape_store_safe(scraper_class, store)
                    )
                    tasks.append(task)
                    store_names.append(store.name)
                    logger.info(f"Created scraping task for {store.name}")
                else:
                    logger.warning(f"No scraper found for {store.name}")
            
            # Execute all scraping tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            all_results = {}
            for i, result in enumerate(results):
                store_name = store_names[i]
                if isinstance(result, Exception):
                    logger.error(f"Scraping failed for {store_name}: {result}")
                    all_results[store_name] = []
                else:
                    all_results[store_name] = result
                    logger.info(f"Scraped {len(result)} products from {store_name}")
            
            # Save all results to database
            total_saved = await self._save_all_results(all_results, db)
            logger.info(f"Saved {total_saved} total products to database")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in scrape_all_stores: {e}")
            return {}
        finally:
            db.close()
    
    async def scrape_single_store(self, store_id: int) -> List[ProductData]:
        """Scrape a specific store by ID"""
        db = SessionLocal()
        try:
            store = db.query(Store).filter(Store.id == store_id).first()
            if not store:
                logger.error(f"Store with ID {store_id} not found")
                return []
            
            if not store.is_active:
                logger.warning(f"Store {store.name} is not active")
                return []
            
            if not store.scraper_module or store.scraper_module not in self.scrapers:
                logger.error(f"No scraper available for {store.name}")
                return []
            
            # Update store status
            store.status = "scraping"
            db.commit()
            
            scraper_class = self.scrapers[store.scraper_module]
            products = await self._scrape_store_safe(scraper_class, store)
            
            # Save results
            saved_count = await self._save_store_results(products, store, db)
            logger.info(f"Saved {saved_count} products from {store.name}")
            
            # Update store status
            store.status = "idle"
            store.last_scraped = datetime.utcnow()
            db.commit()
            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping store {store_id}: {e}")
            # Reset store status on error
            if 'store' in locals():
                store.status = "offline"
                db.commit()
            return []
        finally:
            db.close()
    
    async def _scrape_store_safe(self, scraper_class: Type[BaseScraper], store: Store) -> List[ProductData]:
        """Safely scrape a store with error handling"""
        try:
            logger.info(f"Initializing scraper for {store.name}")
            scraper = scraper_class()
            
            # Update store status
            db = SessionLocal()
            store.status = "scraping"
            db.commit()
            db.close()
            
            products = await scraper.scrape()
            
            logger.info(f"Successfully scraped {len(products)} products from {store.name}")
            
            # Update store status
            db = SessionLocal()
            store.status = "idle"
            store.last_scraped = datetime.utcnow()
            db.commit()
            db.close()
            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping {store.name}: {e}")
            
            # Update store status to offline on error
            db = SessionLocal()
            store.status = "offline"
            db.commit()
            db.close()
            
            return []
    
    async def _save_all_results(self, all_results: Dict[str, List[ProductData]], db: Session) -> int:
        """Save all scraping results to database"""
        total_saved = 0
        
        for store_name, products in all_results.items():
            try:
                store = db.query(Store).filter(Store.name == store_name).first()
                if store:
                    saved = await self._save_store_results(products, store, db)
                    total_saved += saved
            except Exception as e:
                logger.error(f"Error saving results for {store_name}: {e}")
                continue
        
        return total_saved
    
    async def _save_store_results(self, products: List[ProductData], store: Store, db: Session) -> int:
        """Save products from a single store to database"""
        saved_count = 0
        
        try:
            for product_data in products:
                try:
                    # Find or create product
                    product = db.query(Product).filter(
                        Product.name == product_data.name
                    ).first()
                    
                    if not product:
                        product = Product(
                            name=product_data.name,
                            category=product_data.category or "uncategorized",
                            keywords=product_data.name.lower(),
                            is_active=True
                        )
                        db.add(product)
                        db.flush()  # Get the ID
                    
                    # Delete existing price for this product-store combination
                    db.query(Price).filter(
                        Price.product_id == product.id,
                        Price.store_id == store.id
                    ).delete()
                    
                    # Create new price entry
                    price = Price(
                        product_id=product.id,
                        store_id=store.id,
                        price=float(product_data.price) if product_data.price else 0.0,
                        price_per_kg=float(product_data.price_per_kg) if product_data.price_per_kg else None,
                        pack_size=product_data.pack_size,
                        pack_unit=product_data.pack_unit,
                        is_available=product_data.is_available,
                        is_organic=product_data.is_organic,
                        is_discounted=product_data.is_discounted,
                        original_price=float(product_data.original_price) if product_data.original_price else None,
                        brand=product_data.brand,
                        image_url=product_data.image_url,
                        product_url=product_data.product_url,
                        scraped_at=product_data.scraped_at
                    )
                    
                    db.add(price)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving product {product_data.name}: {e}")
                    continue
            
            db.commit()
            logger.info(f"Saved {saved_count} products for {store.name}")
            
        except Exception as e:
            logger.error(f"Error in _save_store_results for {store.name}: {e}")
            db.rollback()
        
        return saved_count
    
    def get_target_products(self) -> List[Dict]:
        """Get the list of target products to track"""
        # Use the same list as defined in base_scraper
        dummy_scraper = self.scrapers["gourmet_scraper"]()
        return dummy_scraper.products_to_track
    
    async def search_product_across_stores(self, product_name: str) -> Dict[str, List[ProductData]]:
        """Search for a specific product across all active stores"""
        logger.info(f"Searching for '{product_name}' across all stores")
        
        db = SessionLocal()
        try:
            active_stores = db.query(Store).filter(Store.is_active == True).all()
            
            tasks = []
            store_names = []
            
            for store in active_stores:
                if store.scraper_module and store.scraper_module in self.scrapers:
                    scraper_class = self.scrapers[store.scraper_module]
                    task = asyncio.create_task(
                        self._search_product_in_store(scraper_class, product_name)
                    )
                    tasks.append(task)
                    store_names.append(store.name)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            search_results = {}
            for i, result in enumerate(results):
                store_name = store_names[i]
                if isinstance(result, Exception):
                    logger.error(f"Search failed for {store_name}: {result}")
                    search_results[store_name] = []
                else:
                    search_results[store_name] = result
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in search_product_across_stores: {e}")
            return {}
        finally:
            db.close()
    
    async def _search_product_in_store(self, scraper_class: Type[BaseScraper], product_name: str) -> List[ProductData]:
        """Search for a product in a specific store"""
        try:
            scraper = scraper_class()
            await scraper.initialize_browser()
            await scraper.page.goto(scraper.base_url)
            results = await scraper.search_product(product_name)
            await scraper.close_browser()
            return results
        except Exception as e:
            logger.error(f"Error searching in {scraper_class.__name__}: {e}")
            return []

# Global instance for use in API routes
scraper_manager = ScraperManager()