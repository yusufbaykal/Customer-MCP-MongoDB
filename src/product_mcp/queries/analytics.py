from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone


class AnalyticsQueries:
    """MongoDB aggregation queries for analytics operations."""
    
    @staticmethod
    def get_top_selling_products(limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products aggregation pipeline."""
        return [
            {"$sort": {"total_sold": -1}},
            {"$limit": limit},
            {"$project": {
                "name": 1,
                "sku": 1,
                "total_sold": 1,
                "price": 1,
                "revenue": {"$multiply": ["$total_sold", "$price"]}
            }}
        ]
    
    @staticmethod
    def get_revenue_by_category() -> List[Dict[str, Any]]:
        """Get revenue by category aggregation pipeline."""
        return [
            {"$group": {
                "_id": "$category",
                "total_revenue": {"$sum": {"$multiply": ["$total_sold", "$price"]}},
                "total_products": {"$sum": 1},
                "avg_price": {"$avg": "$price"}
            }},
            {"$sort": {"total_revenue": -1}}
        ]
    
    @staticmethod
    def get_low_stock_products(threshold: int = 10) -> List[Dict[str, Any]]:
        """Get products with low stock."""
        return [
            {"$match": {"stock_quantity": {"$lt": threshold}}},
            {"$sort": {"stock_quantity": 1}},
            {"$project": {
                "name": 1,
                "sku": 1,
                "stock_quantity": 1,
                "price": 1,
                "category": 1
            }}
        ]
    
    @staticmethod
    def get_sales_summary() -> List[Dict[str, Any]]:
        """Get overall sales summary."""
        return [
            {"$group": {
                "_id": None,
                "total_products": {"$sum": 1},
                "total_revenue": {"$sum": {"$multiply": ["$total_sold", "$price"]}},
                "total_units_sold": {"$sum": "$total_sold"},
                "avg_price": {"$avg": "$price"},
                "categories": {"$addToSet": "$category"}
            }},
            {"$project": {
                "_id": 0,
                "total_products": 1,
                "total_revenue": 1,
                "total_units_sold": 1,
                "avg_price": 1,
                "category_count": {"$size": "$categories"}
            }}
        ] 

    @staticmethod
    def sales_analytics_by_period(period: str, category: Optional[str] = None, include_trends: bool = False) -> List[Dict[str, Any]]:
        """Return a basic pipeline placeholder for sales analytics by period."""
        match_stage: Dict[str, Any] = {}
        if category:
            match_stage["category"] = category
        pipeline: List[Dict[str, Any]] = []
        if match_stage:
            pipeline.append({"$match": match_stage})
        period_mapping: Dict[str, Dict[str, Any]] = {
            "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "week": {"$isoWeek": "$created_at"},
            "month": {"$month": "$created_at"},
            "quarter": {"$ceil": {"$divide": [{"$month": "$created_at"}, 3]}},
            "year": {"$year": "$created_at"}
        }
        period_key: Dict[str, Any] = period_mapping.get(period, {"$year": "$created_at"})
        pipeline.extend([
            {"$group": {
                "_id": period_key,
                "total_revenue": {"$sum": {"$multiply": ["$price", "$total_sold"]}},
                "total_units": {"$sum": "$total_sold"}
            }},
            {"$sort": {"_id": 1}}
        ])
        if include_trends:
            pipeline.append({"$set": {"trend": "n/a"}})
        return pipeline

    @staticmethod
    def category_performance_analysis() -> List[Dict[str, Any]]:
        """Return category performance pipeline."""
        return [
            {"$group": {
                "_id": "$category",
                "total_products": {"$sum": 1},
                "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}},
                "avg_price": {"$avg": "$price"}
            }},
            {"$sort": {"total_value": -1}}
        ]

    @staticmethod
    def price_analysis_by_category() -> List[Dict[str, Any]]:
        """Return price distribution analysis by category."""
        return [
            {"$bucket": {
                "groupBy": "$price",
                "boundaries": [0, 50, 100, 200, 500, 1000, float("inf")],
                "default": "other",
                "output": {
                    "count": {"$sum": 1},
                    "avg_stock": {"$avg": "$stock"}
                }
            }}
        ]

    @staticmethod
    def trending_products_analysis(days: int = 30) -> List[Dict[str, Any]]:
        """Return trending products pipeline placeholder."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return [
            {"$match": {"created_at": {"$gte": cutoff}}},
            {"$sort": {"total_sold": -1}},
            {"$limit": 20}
        ]

    @staticmethod
    def inventory_velocity_analysis() -> List[Dict[str, Any]]:
        """Return inventory velocity pipeline placeholder."""
        return [
            {"$project": {
                "name": 1,
                "sku": 1,
                "stock": 1,
                "velocity": {"$divide": ["$total_sold", {"$max": [1, "$stock"]}]}
            }},
            {"$sort": {"velocity": -1}}
        ] 