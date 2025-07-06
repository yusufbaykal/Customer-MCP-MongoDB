import logging
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

from ..core.database import db_manager
from ..core.models import ProductCreate, ProductUpdate, ProductSearchFilter, ProductCategory, ProductStatus

logger = logging.getLogger(__name__)


class ProductTools:
    """Product management tools for MCP server."""
    
    @staticmethod
    def register_tools(mcp: FastMCP) -> None:  # type: ignore[type-arg]
        """Register all product management tools with the MCP server."""
        
        @mcp.tool()
        def create_product(  # type: ignore[misc]
            name: str,
            price: str,
            stock: str,
            category: str,
            sku: str,
            description: str = "",
            tags: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Create a new product in the inventory.
            
            Args:
                name: Product name (required)
                price: Product price as string (will be converted to float, must be positive)
                stock: Initial stock quantity as string (will be converted to int, non-negative)
                category: Product category (electronics, clothing, food, books, home, sports, health, automotive, toys, other)
                sku: Stock Keeping Unit - unique product identifier
                description: Product description (optional)
                tags: List of tags for search and categorization (optional)
            
            Returns:
                JSON string with operation result and product details
            """
            try:
                try:
                    price_float = float(price)
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "error": f"Invalid price format: '{price}'. Price must be a valid number."
                    }
                try:
                    stock_int = int(stock)
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "error": f"Invalid stock format: '{stock}'. Stock must be a valid integer."
                    }
                
                try:
                    product_category = ProductCategory(category.lower())
                except ValueError:
                    valid_categories = [c.value for c in ProductCategory]
                    return {
                        "success": False,
                        "error": f"Invalid category '{category}'. Valid options: {', '.join(valid_categories)}"
                    }
                
                product_data = ProductCreate(
                    name=name,
                    description=description,
                    price=price_float,
                    stock=stock_int,
                    category=product_category,
                    sku=sku,
                    tags=tags or []
                )

                new_product = db_manager.create_product(product_data)
                
                if new_product:
                    return {
                        "success": True,
                        "message": f"Product '{new_product.name}' created successfully",
                        "data": {
                            "id": new_product.id,
                            "name": new_product.name,
                            "sku": new_product.sku,
                            "price": new_product.price,
                            "stock": new_product.stock,
                            "category": new_product.category.value,
                            "created_at": new_product.created_at.isoformat()
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to create product. SKU may already exist."
                    }
                    
            except Exception as e:
                logger.error(f"Error creating product: {e}")
                return {
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                }
        
        @mcp.tool()
        def get_product(identifier: str, by_sku: bool = False) -> Dict[str, Any]:  # type: ignore[misc]
            """
            Retrieve a product by ID or SKU.
            
            Args:
                identifier: Product ID or SKU
                by_sku: If True, search by SKU; otherwise search by ID
            
            Returns:
                JSON string with product details or error message
            """
            try:
                if by_sku:
                    product = db_manager.get_product_by_sku(identifier)
                else:
                    product = db_manager.get_product_by_id(identifier)
                
                if product:
                    return {
                        "success": True,
                        "data": {
                            "id": product.id,
                            "name": product.name,
                            "description": product.description,
                            "price": product.price,
                            "stock": product.stock,
                            "category": product.category.value,
                            "status": product.status.value,
                            "sku": product.sku,
                            "tags": product.tags,
                            "created_at": product.created_at.isoformat(),
                            "updated_at": product.updated_at.isoformat()
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Product not found with {'SKU' if by_sku else 'ID'}: {identifier}"
                    }
                    
            except Exception as e:
                logger.error(f"Error retrieving product: {e}")
                return {
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                }
        
        @mcp.tool()
        def search_products(  # type: ignore[misc]
            query: str = "",
            category: str = "",
            status: str = "",
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            in_stock_only: bool = False,
            low_stock_only: bool = False,
            limit: int = 20,
            tags: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Search products with various filters.
            
            Args:
                query: Text search in name, description, and tags
                category: Filter by category
                status: Filter by status (active, inactive, out_of_stock, discontinued, draft)
                min_price: Minimum price filter
                max_price: Maximum price filter
                in_stock_only: Show only products with stock > 0
                low_stock_only: Show only products with low stock
                limit: Maximum number of results (1-100)
            
            Returns:
                JSON string with search results
            """
            try:
                search_filter = ProductSearchFilter(
                    query=query if query else None,
                    category=ProductCategory(category) if category else None,
                    status=ProductStatus(status) if status else None,
                    min_price=min_price,
                    max_price=max_price,
                    in_stock_only=in_stock_only,
                    low_stock_only=low_stock_only,
                    limit=min(max(1, limit), 100),
                    tags=tags or []
                )
                
                products = db_manager.search_products(search_filter)
                
                results: List[Dict[str, Any]] = []
                for product in products:
                    results.append({
                        "id": product.id,
                        "name": product.name,
                        "sku": product.sku,
                        "price": product.price,
                        "stock": product.stock,
                        "category": product.category.value,
                        "status": product.status.value
                    })
                
                return {
                    "success": True,
                    "message": f"Found {len(results)} products",
                    "data": {
                        "products": results,
                        "total_found": len(results),
                        "search_params": {
                            "query": query,
                            "category": category,
                            "status": status,
                            "price_range": f"{min_price or 0} - {max_price or 'unlimited'}",
                            "filters": {
                                "in_stock_only": in_stock_only,
                                "low_stock_only": low_stock_only
                            }
                        }
                    }
                }
                
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Invalid parameter: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Error searching products: {e}")
                return {
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                }
        
        @mcp.tool()
        def update_product(  # type: ignore[misc]
            identifier: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            price: Optional[str] = None,
            stock: Optional[str] = None,
            category: Optional[str] = None,
            status: Optional[str] = None,
            tags: Optional[List[str]] = None,
            by_sku: bool = False
        ) -> Dict[str, Any]:
            """
            Update product information.
            
            Args:
                identifier: Product ID or SKU
                name: New product name (optional)
                description: New description (optional)
                price: New price as string (will be converted to float, optional)
                stock: New stock quantity as string (will be converted to int, optional)
                category: New category (optional)
                status: New status (optional)
                tags: New tags list (optional)
                by_sku: If True, identify product by SKU; otherwise by ID
            
            Returns:
                JSON string with operation result
            """
            try:
                if by_sku:
                    product = db_manager.get_product_by_sku(identifier)
                else:
                    product = db_manager.get_product_by_id(identifier)
                
                if not product:
                    return {
                        "success": False,
                        "error": f"Product not found with {'SKU' if by_sku else 'ID'}: {identifier}"
                    }

                assert product.id is not None, "Product ID cannot be None"
                
                update_data = ProductUpdate()  # type: ignore[call-arg]
                
                if name is not None:
                    update_data.name = name
                if description is not None:
                    update_data.description = description
                if price is not None:
                    try:
                        update_data.price = float(price)
                    except (ValueError, TypeError):
                        return {
                            "success": False,
                            "error": f"Invalid price format: '{price}'. Price must be a valid number."
                        }
                if stock is not None:
                    try:
                        update_data.stock = int(stock)
                    except (ValueError, TypeError):
                        return {
                            "success": False,
                            "error": f"Invalid stock format: '{stock}'. Stock must be a valid integer."
                        }
                if category is not None:
                    try:
                        update_data.category = ProductCategory(category.lower())
                    except ValueError:
                        valid_categories = [c.value for c in ProductCategory]
                        return {
                            "success": False,
                            "error": f"Invalid category '{category}'. Valid options: {', '.join(valid_categories)}"
                        }
                if status is not None:
                    try:
                        update_data.status = ProductStatus(status.lower())
                    except ValueError:
                        valid_statuses = [s.value for s in ProductStatus]
                        return {
                            "success": False,
                            "error": f"Invalid status '{status}'. Valid options: {', '.join(valid_statuses)}"
                        }
                if tags is not None:
                    update_data.tags = tags
                
                updated_product = db_manager.update_product(product.id, update_data)
                
                if updated_product:
                    return {
                        "success": True,
                        "message": f"Product '{updated_product.name}' updated successfully",
                        "data": {
                            "id": updated_product.id,
                            "name": updated_product.name,
                            "sku": updated_product.sku,
                            "price": updated_product.price,
                            "stock": updated_product.stock,
                            "category": updated_product.category.value,
                            "status": updated_product.status.value,
                            "updated_at": updated_product.updated_at.isoformat()
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to update product"
                    }
                    
            except Exception as e:
                logger.error(f"Error updating product: {e}")
                return {
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                }
        
        @mcp.tool()
        def delete_product(identifier: str, by_sku: bool = False, confirm: bool = False) -> Dict[str, Any]:  # type: ignore[misc]
            """
            Delete a product from inventory.
            
            Args:
                identifier: Product ID or SKU
                by_sku: If True, identify product by SKU; otherwise by ID
                confirm: Confirmation flag to prevent accidental deletion
            
            Returns:
                JSON string with operation result
            """
            try:
                if not confirm:
                    return {
                        "success": False,
                        "error": "Deletion requires confirmation. Set confirm=True to proceed.",
                        "warning": "This action cannot be undone."
                    }
                
                if by_sku:
                    product = db_manager.get_product_by_sku(identifier)
                else:
                    product = db_manager.get_product_by_id(identifier)
                
                if not product:
                    return {
                        "success": False,
                        "error": f"Product not found with {'SKU' if by_sku else 'ID'}: {identifier}"
                    }

                assert product.id is not None, "Product ID cannot be None"
                
                success = db_manager.delete_product(product.id)
                
                if success:
                    return {
                        "success": True,
                        "message": f"Product '{product.name}' (SKU: {product.sku}) deleted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to delete product"
                    }
                    
            except Exception as e:
                logger.error(f"Error deleting product: {e}")
                return {
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                } 