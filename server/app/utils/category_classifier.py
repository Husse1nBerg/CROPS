# In server/app/utils/category_classifier.py
"""
Category Classifier Utility
Path: backend/app/utils/category_classifier.py
"""
from typing import Dict, List, Optional
import re

class CategoryClassifier:
    """Classifies products into categories based on keywords."""

    def __init__(self):
        self.category_keywords: Dict[str, List[str]] = {
            "A": [
                "cucumber", "خيار", "tomato", "طماطم", "cherry tomato", 
                "capsicum", "pepper", "فلفل", "arugula", "جرجير", 
                "parsley", "بقدونس", "coriander", "كزبرة", "mint", "نعناع", 
                "kale", "basil", "ريحان"
            ],
            "B": [
                "lettuce", "خس", "chives", "ثوم معمر", "batavia"
            ]
        }

    def classify(self, product_name: str) -> str:
        """
        Classify a product into a category based on its name.
        Defaults to 'A' if no specific keywords are found.
        """
        text_to_search = product_name.lower()

        for keyword in self.category_keywords["B"]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_search):
                return "B"
        
        for keyword in self.category_keywords["A"]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_search):
                return "A"
        
        return "A" # Default category