"""
Celery tasks for web scraping - Updated for real-time grocery store scraping
Path: backend/app/tasks/scraping_tasks.py
"""

from celery import shared_task
from celery.schedules import crontab
from datetime import datetime
import logging
import asyncio
from typing import List

from app.database import SessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.scrapers.scraper_manager import scraper_manager

logger = logging.getLogger(__name__)

def setup_periodic_tasks():
    """Setup periodic scraping tasks for real-time grocery data"""
    from app.tasks.celery_app import celery as celery_app
    
    # Schedule scraping every 4 hours for fresh produce (perishable items need frequent updates)
    celery_app.conf.beat_schedule = {
        'scrape-all-stores-frequent': {
            'task': 'app.tasks.scraping_tasks.scrape_all_stores_task',
            'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at the top of the hour
        },
        'scrape-priority-products': {
            'task': 'app.tasks.scraping_tasks.scrape_priority_products_task',
            'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours for high-priority items
        }
    }

@shared_task
def scrape_store_task(store_id: int):
    """Scrape a specific store using the centralized manager"""
    logger.info(f"Starting scrape task for store ID: {store_id}")
    
    # Create event loop for async operation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        products_data = loop.run_until_complete(scraper_manager.scrape_single_store(store_id))
        logger.info(f"Completed scrape task for store ID {store_id}: {len(products_data)} products")
        return len(products_data)
        
    except Exception as e:
        logger.error(f"Error in scrape_store_task for store {store_id}: {e}")
        return 0
    finally:
        loop.close()

@shared_task
def scrape_all_stores_task():
    """Scrape all active stores using the centralized manager"""
    logger.info("Starting scrape task for all active stores")
    
    # Create event loop for async operation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(scraper_manager.scrape_all_stores())
        
        total_products = sum(len(products) for products in results.values())
        logger.info(f"Completed scrape task for all stores: {total_products} total products from {len(results)} stores")
        
        return {
            "stores_scraped": len(results),
            "total_products": total_products,
            "results": {store: len(products) for store, products in results.items()}
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_all_stores_task: {e}")
        return {"error": str(e)}
    finally:
        loop.close()

@shared_task 
def scrape_priority_products_task():
    """Scrape only high-priority Category A products more frequently"""
    logger.info("Starting priority products scraping task")
    
    # Get Category A products (higher priority)
    priority_products = [
        "Tomatoes", "Cherry Tomatoes", "Cucumbers", "Capsicum Red", 
        "Capsicum Yellow", "Arugula", "Parsley", "Coriander", "Mint"
    ]
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        all_results = {}
        for product in priority_products:
            results = loop.run_until_complete(
                scraper_manager.search_product_across_stores(product)
            )
            all_results[product] = results
            
        total_found = sum(
            len(store_results) 
            for product_results in all_results.values() 
            for store_results in product_results.values()
        )
        
        logger.info(f"Priority scraping complete: {total_found} products found")
        return {"priority_products_found": total_found}
        
    except Exception as e:
        logger.error(f"Error in scrape_priority_products_task: {e}")
        return {"error": str(e)}
    finally:
        loop.close()

def trigger_scraping(db):
    """Trigger scraping for all stores (called from API)"""
    stores = db.query(Store).filter(Store.is_active == True).all()
    
    for store in stores:
        scrape_store_task.delay(store.id)
    
    return len(stores)

@shared_task
def search_specific_product_task(product_name: str):
    """Search for a specific product across all stores"""
    logger.info(f"Starting search task for product: {product_name}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(
            scraper_manager.search_product_across_stores(product_name)
        )
        
        total_found = sum(len(store_results) for store_results in results.values())
        logger.info(f"Search complete for '{product_name}': {total_found} products found across {len(results)} stores")
        
        return {
            "product": product_name,
            "total_found": total_found,
            "stores_searched": len(results),
            "results": {store: len(products) for store, products in results.items()}
        }
        
    except Exception as e:
        logger.error(f"Error searching for product '{product_name}': {e}")
        return {"error": str(e)}
    finally:
        loop.close()