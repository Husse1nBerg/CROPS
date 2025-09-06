from celery import Celery
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Create the Celery instance
celery = Celery(
    __name__,
    broker=redis_url,
    backend=redis_url
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Add this alias for compatibility
celery_app = celery