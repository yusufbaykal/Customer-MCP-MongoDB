import json
import logging
from typing import Optional, Any
from fastmcp import FastMCP

from ..core.database import db_manager
from ..core.config import settings
from ..core.models import ProductUpdate
from ..queries.inventory import InventoryQueries

logger = logging.getLogger(__name__)


class InventoryTools:
    """Inventory management tools for stock operations."""
    
    @staticmethod
    def register_tools(mcp: FastMCP) -> None:  # type: ignore[type-arg]
        """Register all inventory tools with the MCP server."""
        
        @mcp.tool()
        def get_inventory_summary() -> str:  # type: ignore[misc]
            """
            Get comprehensive inventory summary with key metrics.
            
            Returns:
                JSON string with complete inventory overview
            """
            try:
                summary = db_manager.get_inventory_summary()
                
                return json.dumps({
                    "success": True,
                    "message": "Inventory summary generated",
                    "data": {
                        "summary_metrics": {
                            "total_products": summary.total_products,
                            "total_inventory_value": round(summary.total_value, 2),
                            "low_stock_alerts": summary.low_stock_products,
                            "out_of_stock_alerts": summary.out_of_stock_products
                        },
                        "categories_breakdown": summary.categories_breakdown,
                        "health_indicators": {
                            "stock_health": "healthy" if summary.low_stock_products < 5 else "needs_attention",
                            "availability_rate": round(
                                ((summary.total_products - summary.out_of_stock_products) / 
                                 max(summary.total_products, 1)) * 100, 1
                            ),
                            "low_stock_threshold": settings.low_stock_threshold
                        },
                        "last_updated": summary.last_updated.isoformat()
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting inventory summary: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def check_low_stock(threshold: Optional[int] = None) -> str:  # type: ignore[misc]
            """
            Check for products with low stock levels.
            
            Args:
                threshold: Custom stock threshold (uses config default if not provided)
            
            Returns:
                JSON string with low stock analysis and recommendations
            """
            try:
                stock_threshold = threshold or settings.low_stock_threshold
                
                if stock_threshold < 0:
                    return json.dumps({
                        "success": False,
                        "error": "Stock threshold must be non-negative"
                    })
                pipeline = InventoryQueries.low_stock_analysis(threshold=stock_threshold)
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                urgency_groups: dict[str, list[dict[str, Any]]] = {
                    "critical": [],
                    "high": [],
                    "medium": [],
                    "low": []
                }
                
                for product in results:
                    urgency = product.get('urgency_level', 'low')
                    urgency_groups[urgency].append(product)
                
                return json.dumps({
                    "success": True,
                    "message": f"Low stock analysis completed (threshold: {stock_threshold})",
                    "data": {
                        "threshold_used": stock_threshold,
                        "total_low_stock": len(results),
                        "urgency_breakdown": {
                            level: len(products) for level, products in urgency_groups.items()
                        },
                        "products_by_urgency": urgency_groups,
                        "recommendations": {
                            "immediate_action_needed": len(urgency_groups["critical"]),
                            "urgent_restock": len(urgency_groups["high"]),
                            "plan_restock": len(urgency_groups["medium"])
                        }
                    }
                })
                
            except Exception as e:
                logger.error(f"Error checking low stock: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def update_stock(identifier: str, new_stock: str, by_sku: bool = False) -> str:  # type: ignore[misc]
            """
            Update stock level for a specific product.
            
            Args:
                identifier: Product ID or SKU
                new_stock: New stock quantity as string (will be converted to int, non-negative)
                by_sku: If True, identify product by SKU; otherwise by ID
            
            Returns:
                JSON string with update result
            """
            try:
                try:
                    stock_int = int(new_stock)
                except (ValueError, TypeError):
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid stock format: '{new_stock}'. Stock must be a valid integer."
                    })
                
                if stock_int < 0:
                    return json.dumps({
                        "success": False,
                        "error": "Stock quantity cannot be negative"
                    })
                if by_sku:
                    product = db_manager.get_product_by_sku(identifier)
                else:
                    product = db_manager.get_product_by_id(identifier)
                
                if not product:
                    return json.dumps({
                        "success": False,
                        "error": f"Product not found with {'SKU' if by_sku else 'ID'}: {identifier}"
                    })
 
                assert product.id is not None, "Product ID cannot be None"
                old_stock = product.stock
                
                update_data = ProductUpdate(stock=stock_int)  # type: ignore[call-arg]
                
                updated_product = db_manager.update_product(product.id, update_data)
                
                if updated_product:
                    change = stock_int - old_stock
                    change_type = "increased" if change > 0 else "decreased" if change < 0 else "unchanged"
                    alerts: list[str] = []
                    if stock_int == 0:
                        alerts.append("CRITICAL: Product is now out of stock")
                    elif stock_int <= settings.low_stock_threshold:
                        alerts.append(f"WARNING: Stock is below threshold ({settings.low_stock_threshold})")
                    
                    return json.dumps({
                        "success": True,
                        "message": f"Stock updated for '{updated_product.name}'",
                        "data": {
                            "product": {
                                "name": updated_product.name,
                                "sku": updated_product.sku,
                                "id": updated_product.id
                            },
                            "stock_change": {
                                "old_stock": old_stock,
                                "new_stock": stock_int,
                                "change": change,
                                "change_type": change_type
                            },
                            "alerts": alerts,
                            "updated_at": updated_product.updated_at.isoformat()
                        }
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Failed to update stock"
                    })
                    
            except Exception as e:
                logger.error(f"Error updating stock: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def get_stock_distribution() -> str:  # type: ignore[misc]
            """
            Analyze stock distribution across categories.
            
            Returns:
                JSON string with detailed stock distribution analysis
            """
            try:
                pipeline = InventoryQueries.stock_distribution_by_category()
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                return json.dumps({
                    "success": True,
                    "message": "Stock distribution analysis completed",
                    "data": {
                        "distribution_analysis": results,
                        "categories_analyzed": len(results),
                        "analysis_type": "category_based_distribution"
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting stock distribution: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def analyze_inventory_turnover(days: int = 90) -> str:  # type: ignore[misc]
            """
            Analyze inventory turnover and product velocity.
            
            Args:
                days: Number of days for turnover analysis
            
            Returns:
                JSON string with turnover analysis
            """
            try:
                if days < 1 or days > 365:
                    return json.dumps({
                        "success": False,
                        "error": "Days parameter must be between 1 and 365"
                    })
                
                pipeline = InventoryQueries.inventory_turnover_analysis(days=days)
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                turnover_groups: dict[str, list[dict[str, Any]]] = {
                    "fast_moving": [],
                    "medium_moving": [],
                    "slow_moving": [],
                    "out_of_stock": []
                }
                
                for product in results:
                    classification = product.get('turnover_classification', 'unknown')
                    if classification in turnover_groups:
                        turnover_groups[classification].append(product)
                
                return json.dumps({
                    "success": True,
                    "message": f"Inventory turnover analysis for {days} days",
                    "data": {
                        "analysis_period_days": days,
                        "turnover_breakdown": {
                            classification: len(products) 
                            for classification, products in turnover_groups.items()
                        },
                        "products_by_turnover": turnover_groups,
                        "total_products_analyzed": len(results)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error analyzing inventory turnover: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def get_stock_alerts_dashboard() -> str:  # type: ignore[misc]
            """
            Get comprehensive stock alerts dashboard.
            
            Returns:
                JSON string with prioritized stock alerts and recommendations
            """
            try:
                pipeline = InventoryQueries.stock_alert_dashboard()
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                alert_groups: dict[str, list[dict[str, Any]]] = {
                    "critical": [],
                    "high": [],
                    "medium": [],
                    "overstocked": []
                }
                
                for alert in results:
                    alert_level = alert.get('stock_info', {}).get('alert_level', 'unknown')
                    if alert_level in alert_groups:
                        alert_groups[alert_level].append(alert)
                
                return json.dumps({
                    "success": True,
                    "message": "Stock alerts dashboard generated",
                    "data": {
                        "alert_summary": {
                            level: len(alerts) for level, alerts in alert_groups.items()
                        },
                        "alerts_by_priority": alert_groups,
                        "total_alerts": len(results),
                        "dashboard_generated_at": db_manager.get_inventory_summary().last_updated.isoformat()
                    }
                })
                
            except Exception as e:
                logger.error(f"Error generating stock alerts dashboard: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                }) 