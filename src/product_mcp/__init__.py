__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.config import settings
from .core.database import DatabaseManager
from .core.models import Product, ProductCategory, ProductStatus

__all__ = [
    "settings",
    "DatabaseManager", 
    "Product",
    "ProductCategory",
    "ProductStatus",
] 