from datetime import datetime
from enum import Enum
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ProductCategory(str, Enum):
    """Product categories with standardized values."""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BOOKS = "books"
    HOME = "home"
    SPORTS = "sports"
    HEALTH = "health"
    AUTOMOTIVE = "automotive"
    TOYS = "toys"
    OTHER = "other"


class ProductStatus(str, Enum):
    """Product status for lifecycle management."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"


class ProductBase(BaseModel):
    """Base product model with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    category: ProductCategory = Field(..., description="Product category")
    sku: str = Field(..., min_length=1, max_length=50, description="Stock Keeping Unit (unique)")
    tags: List[str] = Field(default_factory=list, description="Product tags for search")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> List[str]:
        """Validate and clean tags."""
        if not v:
            return []
        return list(set(tag.strip().lower() for tag in v if tag.strip()))
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v: str) -> str:
        """Validate SKU format."""
        if not v.strip():
            raise ValueError("SKU cannot be empty")
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError("SKU can only contain letters, numbers, hyphens, and underscores")
        return v.upper()


class ProductCreate(ProductBase):
    """Model for creating new products."""
    stock: int = Field(..., ge=0, description="Initial stock quantity")


class ProductUpdate(BaseModel):
    """Model for updating existing products."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[ProductCategory] = None
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = Field(None, description="Product tags for search")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and clean tags."""
        if v is None:
            return None
        return list(set(tag.strip().lower() for tag in v if tag.strip()))


class Product(ProductBase):
    """Complete product model with all fields."""
    id: Optional[str] = Field(None, description="Product ID (assigned by database)")
    stock: int = Field(..., ge=0, description="Current stock quantity")
    status: ProductStatus = Field(default=ProductStatus.ACTIVE, description="Product status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        json_encoders = {  # type: ignore[misc]
            datetime: lambda v: v.isoformat()  # type: ignore[misc]
        }
        schema_extra = {  # type: ignore[misc]
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 199.99,
                "stock": 50,
                "category": "electronics",
                "status": "active",
                "sku": "WH-001",
                "tags": ["wireless", "audio", "electronics"],
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }


class InventorySummary(BaseModel):
    """Inventory summary statistics."""
    total_products: int = Field(..., description="Total number of products")
    total_value: float = Field(..., description="Total inventory value")
    low_stock_products: int = Field(..., description="Number of products below threshold")
    out_of_stock_products: int = Field(..., description="Number of out-of-stock products")
    categories_breakdown: List[Dict[str, Any]] = Field(..., description="Per-category statistics")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last calculation time")


class ProductSearchFilter(BaseModel):
    """Search and filter parameters for products."""
    query: Optional[str] = Field(None, description="Text search query")
    category: Optional[ProductCategory] = Field(None, description="Filter by category")
    status: Optional[ProductStatus] = Field(None, description="Filter by status")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, gt=0, description="Maximum price filter")
    in_stock_only: bool = Field(default=False, description="Show only products in stock")
    low_stock_only: bool = Field(default=False, description="Show only low stock products")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results to return")
    skip: int = Field(default=0, ge=0, description="Number of results to skip")


class AnalyticsRequest(BaseModel):
    """Request parameters for analytics queries."""
    period: str = Field(..., description="Time period (day, week, month, quarter, year)")
    category: Optional[ProductCategory] = Field(None, description="Filter by category")
    include_trends: bool = Field(default=False, description="Include trend analysis")
    include_forecasts: bool = Field(default=False, description="Include forecasting data")


class OperationResult(BaseModel):
    """Standard operation result model."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional result data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")
    
    class Config:
        json_serializers = {  # type: ignore[misc]
            datetime: lambda v: v.isoformat()  # type: ignore[misc]
        } 