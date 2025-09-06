# In backend/app/utils/seeder.py
"""
Database seeder to populate initial data
Path: backend/app/utils/seeder.py
Usage: python -m app.utils.seeder
"""
import json
import sys
from pathlib import Path
from dotenv import load_dotenv # Import the function

# Add these lines for debugging
from app.config import settings
print(f"DEBUG: The DATABASE_URL being used is: {settings.DATABASE_URL}")
# End of debug lines

# Add parent directory to path and load environment variables
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.product import Product
from app.models.store import Store
from app.api.auth import get_password_hash # Assuming auth service might not be ideal here

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Initialize database tables
        print("Attempting to create database tables...")
        init_db()
        print("✅ Database tables created")
        
        # Seed admin user
        if not db.query(User).filter(User.email == "admin@cropsegypt.com").first():
            admin = User(
                email="admin@cropsegypt.com",
                username="admin",
                hashed_password=get_password_hash("admin123456"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            print("✅ Admin user created (admin@cropsegypt.com / admin123456)")
        
        # ... (rest of the seeder code remains the same) ...

        db.commit()
        print("\n🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()