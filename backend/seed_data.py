"""
Database setup script - creates tables and initial stores configuration
This script no longer contains hardcoded product data - all data comes from real-time scraping
Run with: python seed_data.py
"""

import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.product import Product
from app.models.store import Store
from app.models.price import Price
from app.api.auth import get_password_hash

def setup_database():
    """Setup the database with stores configuration only - NO hardcoded products"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Setting up database for real-time scraping...")
        
        # 1. Create test user (for API access)
        if not db.query(User).filter(User.email == "admin@crops.com").first():
            admin_user = User(
                email="admin@crops.com",
                username="admin",
                full_name="CROPS Admin",
                hashed_password=get_password_hash("crops2025"),
                is_active=True
            )
            db.add(admin_user)
            print("Created admin user: admin@crops.com / crops2025")
        
        # 2. Setup real grocery stores for scraping
        stores_data = [
            {
                "name": "Gourmet Egypt",
                "url": "https://gourmetegypt.com/",
                "type": "grocery",
                "scraper_module": "gourmet_scraper"
            },
            {
                "name": "RDNA Store",
                "url": "https://www.rdnastore.com/",
                "type": "grocery", 
                "scraper_module": "rdna_scraper"
            },
            {
                "name": "Metro Markets",
                "url": "https://www.metro-markets.com/",
                "type": "grocery",
                "scraper_module": "metro_scraper"
            },
            {
                "name": "Spinneys Egypt",
                "url": "https://spinneys-egypt.com/en",
                "type": "grocery",
                "scraper_module": "spinneys_scraper"
            },
            {
                "name": "Rabbit Mart",
                "url": "https://www.rabbitmart.com/eg/",
                "type": "grocery",
                "scraper_module": "rabbit_scraper"
            },
            {
                "name": "Talabat LuLu Hypermarket",
                "url": "https://www.talabat.com/egypt/lulu-hypermarket-tagammoa-1--el-nakhil",
                "type": "grocery",
                "scraper_module": "talabat_scraper"
            },
            {
                "name": "Talabat Mahmoud Elfar",
                "url": "https://www.talabat.com/ar/egypt/mahmoud-elfar",
                "type": "grocery",
                "scraper_module": "talabat_scraper"
            },
            {
                "name": "Instashop",
                "url": "https://instashop.com/en-eg",
                "type": "grocery",
                "scraper_module": "instashop_scraper"
            },
            {
                "name": "Breadfast",
                "url": "https://apps.apple.com/us/app/breadfast-groceries-and-more/id1288436997",
                "type": "grocery",
                "scraper_module": "breadfast_scraper"
            }
        ]
        
        stores = []
        for store_data in stores_data:
            store = db.query(Store).filter(Store.name == store_data["name"]).first()
            if not store:
                store = Store(
                    name=store_data["name"],
                    url=store_data["url"],
                    type=store_data["type"],
                    scraper_module=store_data.get("scraper_module"),
                    is_active=True,
                    status="idle"
                )
                db.add(store)
                stores.append(store)
                print(f"Added store: {store_data['name']}")
            else:
                # Update URL if it changed
                store.url = store_data["url"]
                store.scraper_module = store_data.get("scraper_module")
                stores.append(store)
                print(f"Updated store: {store_data['name']}")
        
        db.commit()
        
        # Print summary
        total_users = db.query(User).count()
        total_stores = db.query(Store).count()
        total_products = db.query(Product).count()
        total_prices = db.query(Price).count()
        
        print("\n" + "="*50)
        print("DATABASE SETUP COMPLETE - REAL-TIME SCRAPING MODE")
        print("="*50)
        print(f"Users: {total_users}")
        print(f"Stores: {total_stores}")
        print(f"Products: {total_products} (from live scraping)")
        print(f"Prices: {total_prices} (from live scraping)")
        print("\nAdmin credentials:")
        print("   Email: admin@crops.com")
        print("   Password: crops2025")
        print("\n" + "="*50)
        print("TARGET PRODUCTS TO TRACK:")
        print("="*50)
        
        # Display the products that will be tracked
        category_a = [
            "Cucumbers", "Tomatoes", "Cherry Tomatoes", 
            "Capsicum Red and Yellow Mix", "Capsicum Red", "Capsicum Yellow",
            "Chili Pepper", "Arugula", "Parsley", "Coriander", "Mint", 
            "Tuscan Kale", "Italian Basil"
        ]
        
        category_b = [
            "Colored Cherry Tomatoes", "Capsicum Green", "Italian Arugula",
            "Chives", "Curly Kale", "Batavia Lettuce", "Ice Berg Lettuce",
            "Oak Leaf Lettuce", "Romain Lettuce"
        ]
        
        print("CATEGORY A:")
        for item in category_a:
            print(f"  • {item}")
        
        print("\nCATEGORY B:")  
        for item in category_b:
            print(f"  • {item}")
            
        print("\n" + "="*50)
        print("STORES TO SCRAPE:")
        print("="*50)
        for store in stores:
            print(f"  • {store.name}")
            print(f"    URL: {store.url}")
        
        print("\n" + "="*50)
        print("NEXT STEPS:")
        print("="*50)
        print("1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("2. Trigger scraping via API: POST /api/scraper/trigger")
        print("3. Monitor scraping status: GET /api/scraper/status")
        print("4. View scraped products: GET /api/products/")
        print("5. Set up automated scraping with Celery beat")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()

# Also expose the function as seed_data for backwards compatibility
def seed_data():
    return setup_database()