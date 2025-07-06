import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, IndexModel
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError,ConnectionFailure
from bson import ObjectId

from .config import settings
from .models import (
    Product, ProductCreate, ProductUpdate, 
    ProductStatus, InventorySummary, ProductSearchFilter
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Professional MongoDB manager with connection pooling and error handling.
    
    Provides high-level operations for product management with proper
    indexing, validation, and query optimization.
    """
    
    def __init__(self, connection_uri: Optional[str] = None, database_name: Optional[str] = None):
        """Initialize database connection with configuration."""
        self.connection_uri = connection_uri or settings.mongodb_uri
        self.database_name = database_name or settings.database_name
        
        self.client: Optional[MongoClient[dict[str, Any]]] = None
        self.db: Optional[Database[dict[str, Any]]] = None
        self.products: Optional[Collection[dict[str, Any]]] = None
        self._connected = False
        
        self.connect()
    
    def connect(self) -> None:
        """Establish database connection with retry logic."""
        try:
            self.client = MongoClient(
                self.connection_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,         
                maxPoolSize=10,                 
                retryWrites=True,               
                retryReads=True                 
            )
            
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.products = self.db.products
            
            self._create_indexes()
            
            self._connected = True
            logger.info(f"Successfully connected to MongoDB: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database connection: {e}")
            raise
    
    def _create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            indexes = [
                IndexModel([("sku", 1)], unique=True, name="sku_unique"),
                
                IndexModel([
                    ("name", "text"),
                    ("description", "text"),
                    ("tags", "text")
                ], name="text_search"),
                
                IndexModel([("category", 1)], name="category_idx"),
                IndexModel([("status", 1)], name="status_idx"),
                IndexModel([("price", 1)], name="price_idx"),
                IndexModel([("stock", 1)], name="stock_idx"),                
                IndexModel([
                    ("category", 1),
                    ("status", 1),
                    ("stock", 1)
                ], name="category_status_stock_idx"),                
                IndexModel([("created_at", -1)], name="created_at_idx"),
                IndexModel([("updated_at", -1)], name="updated_at_idx"),
            ]
            
            self.products.create_indexes(indexes)
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            assert self.client is not None, "Database client not initialized"
            assert self.db is not None, "Database not initialized"
            assert self.products is not None, "Products collection not initialized"
            
            self.client.admin.command('ping')
            
            stats = self.db.command('dbStats')
            
            collection_stats = self.db.command('collStats', 'products')
            
            return {
                "status": "healthy",
                "connected": True,
                "database": self.database_name,
                "total_products": self.products.count_documents({}),
                "database_size": stats.get('dataSize', 0),
                "collection_size": collection_stats.get('size', 0),
                "index_count": len(collection_stats.get('indexSizes', {})),
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def create_product(self, product_data: ProductCreate) -> Optional[Product]:
        """Create a new product with validation."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            product_dict = product_data.model_dump()
            now = datetime.now()
            product_dict.update({
                "status": ProductStatus.ACTIVE,
                "created_at": now,
                "updated_at": now
            })
            
            result = self.products.insert_one(product_dict)
            
            if result.inserted_id:
                created_product = self.products.find_one({"_id": result.inserted_id})
                if created_product:
                    created_product["id"] = str(created_product["_id"])
                    del created_product["_id"]
                    return Product(**created_product)
            
            return None
            
        except DuplicateKeyError:
            logger.warning(f"Duplicate SKU attempted: {product_data.sku}")
            return None
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return None
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Retrieve product by ID."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            product_data = self.products.find_one({"_id": ObjectId(product_id)})
            if product_data:
                product_data["id"] = str(product_data["_id"])
                del product_data["_id"]
                return Product(**product_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {e}")
            return None
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Retrieve product by SKU."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            product_data = self.products.find_one({"sku": sku.upper()})
            if product_data:
                product_data["id"] = str(product_data["_id"])
                del product_data["_id"]
                return Product(**product_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving product by SKU {sku}: {e}")
            return None
    
    def search_products(self, search_filter: ProductSearchFilter) -> List[Product]:
        """Advanced product search with filters."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            query = {}
            
            if search_filter.query:
                query["$text"] = {"$search": search_filter.query}
            
            if search_filter.category:
                query["category"] = search_filter.category
            
            if search_filter.status:
                query["status"] = search_filter.status
            
            if search_filter.min_price is not None or search_filter.max_price is not None:
                price_query = {}
                if search_filter.min_price is not None:
                    price_query["$gte"] = search_filter.min_price
                if search_filter.max_price is not None:
                    price_query["$lte"] = search_filter.max_price
                query["price"] = price_query
            
            if search_filter.in_stock_only:
                query["stock"] = {"$gt": 0}
            elif search_filter.low_stock_only:
                query["stock"] = {"$lte": settings.low_stock_threshold}
            
            if search_filter.tags:
                query["tags"] = {"$in": search_filter.tags}
            
            cursor = self.products.find(query)
            
            if search_filter.query:
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
            else:
                cursor = cursor.sort("name", 1)
            
            cursor = cursor.skip(search_filter.skip).limit(search_filter.limit)
            
            products: List[Product] = []
            for product_data in cursor:
                product_data["id"] = str(product_data["_id"])
                del product_data["_id"]
                products.append(Product(**product_data))
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def update_product(self, product_id: str, update_data: ProductUpdate) -> Optional[Product]:
        """Update product with validation."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            if not update_dict:
                return self.get_product_by_id(product_id)
            
            update_dict["updated_at"] = datetime.now()
            
            result = self.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return self.get_product_by_id(product_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            return None
    
    def delete_product(self, product_id: str) -> bool:
        """Delete product by ID."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            result = self.products.delete_one({"_id": ObjectId(product_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False
    
    def get_inventory_summary(self) -> InventorySummary:
        """Get comprehensive inventory summary using aggregation."""
        try:
            assert self.products is not None, "Products collection not initialized"
            
            pipeline: List[Dict[str, Any]] = [
                {
                    "$group": {
                        "_id": None,
                        "total_products": {"$sum": 1},
                        "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}},
                        "low_stock_count": {
                            "$sum": {
                                "$cond": [
                                    {"$lte": ["$stock", settings.low_stock_threshold]},
                                    1, 0
                                ]
                            }
                        },
                        "out_of_stock_count": {
                            "$sum": {
                                "$cond": [{"$eq": ["$stock", 0]}, 1, 0]
                            }
                        }
                    }
                }
            ]
            
            summary_result: List[Dict[str, Any]] = list(self.products.aggregate(pipeline))
            
            category_pipeline: List[Dict[str, Any]] = [
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1},
                        "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}},
                        "avg_price": {"$avg": "$price"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            categories: List[Dict[str, Any]] = list(self.products.aggregate(category_pipeline))
            
            if summary_result:
                summary = summary_result[0]
                return InventorySummary(
                    total_products=summary.get("total_products", 0),
                    total_value=summary.get("total_value", 0.0),
                    low_stock_products=summary.get("low_stock_count", 0),
                    out_of_stock_products=summary.get("out_of_stock_count", 0),
                    categories_breakdown=categories
                )
            else:
                return InventorySummary(
                    total_products=0,
                    total_value=0.0,
                    low_stock_products=0,
                    out_of_stock_products=0,
                    categories_breakdown=[]
                )
                
        except Exception as e:
            logger.error(f"Error generating inventory summary: {e}")
            return InventorySummary(
                total_products=0,
                total_value=0.0,
                low_stock_products=0,
                out_of_stock_products=0,
                categories_breakdown=[]
            )
    
    def close(self) -> None:
        """Close database connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Database connection closed")


db_manager = DatabaseManager() 