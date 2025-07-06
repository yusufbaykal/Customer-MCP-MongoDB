import json
import logging
from typing import Optional, Any
from fastmcp import FastMCP

from ..core.database import db_manager
from ..core.models import ProductCategory
from ..queries.analytics import AnalyticsQueries

logger = logging.getLogger(__name__)


class AnalyticsTools:
    """Analytics tools for business intelligence and reporting."""
    
    @staticmethod
    def register_tools(mcp: FastMCP) -> None:  # type: ignore[type-arg]
        """Register all analytics tools with the MCP server."""
        
        @mcp.tool()
        def get_sales_analytics(  # type: ignore[misc]
            period: str = "month",
            category: Optional[str] = None,
            include_trends: bool = False
        ) -> str:
            """
            Get sales analytics and performance metrics.
            
            Args:
                period: Time period for analysis (day, week, month, quarter, year)
                category: Optional category filter
                include_trends: Include trend analysis and calculations
            
            Returns:
                JSON string with comprehensive sales analytics
            """
            try:
                valid_periods = ["day", "week", "month", "quarter", "year"]
                if period not in valid_periods:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid period '{period}'. Valid options: {', '.join(valid_periods)}"
                    })
                
                product_category = None
                if category:
                    try:
                        product_category = ProductCategory(category.lower())
                    except ValueError:
                        valid_categories = [c.value for c in ProductCategory]
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid category '{category}'. Valid options: {', '.join(valid_categories)}"
                        })
                
                pipeline = AnalyticsQueries.sales_analytics_by_period(
                    period=period,
                    category=product_category,
                    include_trends=include_trends
                )
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                return json.dumps({
                    "success": True,
                    "message": f"Sales analytics for {period} period",
                    "data": {
                        "period": period,
                        "category_filter": category,
                        "include_trends": include_trends,
                        "analytics": results,
                        "total_periods": len(results)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting sales analytics: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def get_category_analytics() -> str:  # type: ignore[misc]
            """
            Get comprehensive category performance analysis.
            
            Returns:
                JSON string with category-wise performance metrics
            """
            try:
                pipeline = AnalyticsQueries.category_performance_analysis()
            
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                total_categories = len(results)
                total_value = sum(cat.get('total_value', 0) for cat in results)
                total_products = sum(cat.get('total_products', 0) for cat in results)
                
                return json.dumps({
                    "success": True,
                    "message": "Category performance analysis completed",
                    "data": {
                        "summary": {
                            "total_categories": total_categories,
                            "total_portfolio_value": round(total_value, 2),
                            "total_products": total_products,
                            "avg_value_per_category": round(total_value / max(total_categories, 1), 2)
                        },
                        "category_analysis": results
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting category analytics: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def get_price_analysis() -> str:  # type: ignore[misc]
            """
            Get detailed price analysis and distribution metrics.
            
            Returns:
                JSON string with price analysis by category
            """
            try:
                pipeline = AnalyticsQueries.price_analysis_by_category()
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                return json.dumps({
                    "success": True,
                    "message": "Price analysis completed",
                    "data": {
                        "price_analysis": results,
                        "analysis_type": "category_based",
                        "total_categories_analyzed": len(results)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting price analysis: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def get_trending_products(days: int = 30) -> str:  # type: ignore[misc]
            """
            Analyze trending products based on recent activity.
            
            Args:
                days: Number of days to look back for trend analysis
            
            Returns:
                JSON string with trending products analysis
            """
            try:
                if days < 1 or days > 365:
                    return json.dumps({
                        "success": False,
                        "error": "Days parameter must be between 1 and 365"
                    })
                
                pipeline = AnalyticsQueries.trending_products_analysis(days=days)
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                return json.dumps({
                    "success": True,
                    "message": f"Trending products analysis for last {days} days",
                    "data": {
                        "analysis_period_days": days,
                        "trending_products": results,
                        "total_trending": len(results)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting trending products: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def get_inventory_velocity() -> str:  # type: ignore[misc]
            """
            Analyze inventory turnover and velocity metrics.
            
            Returns:
                JSON string with inventory velocity analysis
            """
            try:
                pipeline = AnalyticsQueries.inventory_velocity_analysis()
                
                results: list[dict[str, Any]] = list(db_manager.products.aggregate(pipeline))  # type: ignore[union-attr]
                
                return json.dumps({
                    "success": True,
                    "message": "Inventory velocity analysis completed",
                    "data": {
                        "velocity_analysis": results,
                        "categories_analyzed": len(results),
                        "analysis_type": "turnover_and_velocity"
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting inventory velocity: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                })
        
        @mcp.tool()
        def generate_executive_summary() -> str:  # type: ignore[misc]
            """
            Generate executive summary with key business metrics.
            
            Returns:
                JSON string with executive-level insights
            """
            try:
                category_pipeline = AnalyticsQueries.category_performance_analysis()
                
                category_results: list[dict[str, Any]] = list(db_manager.products.aggregate(category_pipeline))  # type: ignore[union-attr]
                
                inventory_summary = db_manager.get_inventory_summary()
                
                top_category = category_results[0] if category_results else None
                total_portfolio_value = sum(cat.get('total_value', 0) for cat in category_results)
                
                executive_summary: dict[str, Any] = {
                    "key_metrics": {
                        "total_products": inventory_summary.total_products,
                        "portfolio_value": round(total_portfolio_value, 2),
                        "low_stock_alerts": inventory_summary.low_stock_products,
                        "out_of_stock_alerts": inventory_summary.out_of_stock_products
                    },
                    "top_performing_category": {
                        "name": top_category.get('category') if top_category else None,
                        "value": top_category.get('total_value') if top_category else 0,
                        "products": top_category.get('total_products') if top_category else 0
                    },
                    "operational_status": {
                        "categories_active": len(category_results),
                        "inventory_health": "healthy" if inventory_summary.low_stock_products < 5 else "needs_attention",
                        "diversification": len(category_results)
                    },
                    "recommendations": []
                }
            
                if inventory_summary.out_of_stock_products > 0:
                    executive_summary["recommendations"].append({
                        "priority": "high",
                        "action": "urgent_restocking",
                        "details": f"{inventory_summary.out_of_stock_products} products are out of stock"
                    })
                
                if inventory_summary.low_stock_products > 10:
                    executive_summary["recommendations"].append({
                        "priority": "medium",
                        "action": "inventory_planning",
                        "details": f"{inventory_summary.low_stock_products} products have low stock"
                    })
                
                return json.dumps({
                    "success": True,
                    "message": "Executive summary generated",
                    "data": executive_summary
                })
                
            except Exception as e:
                logger.error(f"Error generating executive summary: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Internal error: {str(e)}"
                }) 