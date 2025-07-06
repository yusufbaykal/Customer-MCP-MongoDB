from datetime import datetime
from typing import Dict, List, Any, Optional
from ..core.config import settings


class InventoryQueries:
    """Template-based inventory queries for stock management."""
    
    @staticmethod
    def low_stock_analysis(threshold: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze products below stock threshold."""
        stock_threshold = threshold or settings.low_stock_threshold
        
        return [
            {
                "$match": {
                    "stock": {"$lte": stock_threshold},
                    "status": {"$ne": "discontinued"}
                }
            },
            {
                "$addFields": {
                    "urgency_level": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$stock", 0]}, "then": "critical"},
                                {"case": {"$lte": ["$stock", 5]}, "then": "high"},
                                {"case": {"$lte": ["$stock", stock_threshold]}, "then": "medium"}
                            ],
                            "default": "low"
                        }
                    },
                    "reorder_priority": {
                        "$multiply": [
                            "$price",
                            {"$subtract": [stock_threshold, "$stock"]}
                        ]
                    }
                }
            },
            {
                "$project": {
                    "name": 1,
                    "sku": 1,
                    "category": 1,
                    "current_stock": "$stock",
                    "price": 1,
                    "urgency_level": 1,
                    "reorder_priority": {"$round": ["$reorder_priority", 2]},
                    "estimated_days_left": {
                        "$cond": [
                            {"$eq": ["$stock", 0]},
                            0,
                            {"$multiply": ["$stock", 30]}
                        ]
                    },
                    "potential_lost_revenue": {
                        "$round": [
                            {"$multiply": [
                                "$price",
                                {"$subtract": [stock_threshold, "$stock"]}
                            ]},
                            2
                        ]
                    }
                }
            },
            {
                "$sort": {"reorder_priority": -1}
            }
        ]
    
    @staticmethod
    def stock_distribution_by_category() -> List[Dict[str, Any]]:
        """Analyze stock distribution across categories."""
        return [
            {
                "$group": {
                    "_id": "$category",
                    "total_stock": {"$sum": "$stock"},
                    "total_products": {"$sum": 1},
                    "avg_stock_per_product": {"$avg": "$stock"},
                    "stock_values": {"$push": "$stock"},
                    "total_stock_value": {"$sum": {"$multiply": ["$stock", "$price"]}},
                    "zero_stock_count": {
                        "$sum": {"$cond": [{"$eq": ["$stock", 0]}, 1, 0]}
                    },
                    "low_stock_count": {
                        "$sum": {"$cond": [
                            {"$and": [
                                {"$gt": ["$stock", 0]},
                                {"$lte": ["$stock", settings.low_stock_threshold]}
                            ]},
                            1, 0
                        ]}
                    }
                }
            },
            {
                "$project": {
                    "category": "$_id",
                    "total_stock": 1,
                    "total_products": 1,
                    "avg_stock_per_product": {"$round": ["$avg_stock_per_product", 1]},
                    "total_stock_value": {"$round": ["$total_stock_value", 2]},
                    "stock_health": {
                        "zero_stock_products": "$zero_stock_count",
                        "low_stock_products": "$low_stock_count",
                        "healthy_stock_products": {
                            "$subtract": [
                                "$total_products",
                                {"$add": ["$zero_stock_count", "$low_stock_count"]}
                            ]
                        }
                    },
                    "stock_concentration": {
                        "min": {"$min": "$stock_values"},
                        "max": {"$max": "$stock_values"},
                        "median": {
                            "$arrayElemAt": [
                                {"$slice": [
                                    {"$sortArray": {"input": "$stock_values", "sortBy": 1}},
                                    {"$floor": {"$divide": ["$total_products", 2]}},
                                    1
                                ]},
                                0
                            ]
                        }
                    },
                    "_id": 0
                }
            },
            {
                "$sort": {"total_stock_value": -1}
            }
        ]
    
    @staticmethod
    def inventory_turnover_analysis(days: int = 90) -> List[Dict[str, Any]]:
        """Calculate inventory turnover metrics."""
        
        return [
            {
                "$addFields": {
                    "days_in_inventory": {
                        "$divide": [
                            {"$subtract": [datetime.now(), "$created_at"]},
                            1000 * 60 * 60 * 24
                        ]
                    },
                    "inventory_value": {"$multiply": ["$stock", "$price"]},
                    "turnover_score": {
                        "$cond": [
                            {"$eq": ["$stock", 0]},
                            0,
                            {"$divide": [
                                {"$multiply": ["$price", 365]},
                                {"$multiply": [
                                    {"$divide": [
                                        {"$subtract": [datetime.now(), "$created_at"]},
                                        1000 * 60 * 60 * 24
                                    ]},
                                    {"$multiply": ["$stock", "$price"]}
                                ]}
                            ]}
                        ]
                    }
                }
            },
            {
                "$project": {
                    "name": 1,
                    "sku": 1,
                    "category": 1,
                    "stock": 1,
                    "price": 1,
                    "inventory_value": {"$round": ["$inventory_value", 2]},
                    "days_in_inventory": {"$round": ["$days_in_inventory", 0]},
                    "turnover_classification": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$stock", 0]}, "then": "out_of_stock"},
                                {"case": {"$gt": ["$days_in_inventory", 180]}, "then": "slow_moving"},
                                {"case": {"$gt": ["$days_in_inventory", 90]}, "then": "medium_moving"},
                                {"case": {"$lte": ["$days_in_inventory", 90]}, "then": "fast_moving"}
                            ],
                            "default": "unknown"
                        }
                    },
                    "restock_recommendation": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$stock", 0]}, "then": "urgent_restock"},
                                {"case": {"$lte": ["$stock", 5]}, "then": "restock_soon"},
                                {"case": {"$gt": ["$days_in_inventory", 180]}, "then": "reduce_stock"},
                                {"case": {"$gt": ["$days_in_inventory", 90]}, "then": "monitor_closely"}
                            ],
                            "default": "maintain_current"
                        }
                    }
                }
            },
            {
                "$sort": {"days_in_inventory": -1}
            }
        ]
    
    @staticmethod
    def warehouse_space_utilization() -> List[Dict[str, Any]]:
        """Analyze warehouse space utilization by category."""
        return [
            {
                "$group": {
                    "_id": "$category",
                    "total_units": {"$sum": "$stock"},
                    "total_value": {"$sum": {"$multiply": ["$stock", "$price"]}},
                    "product_count": {"$sum": 1},
                    "avg_unit_value": {"$avg": "$price"}
                }
            },
            {
                "$project": {
                    "category": "$_id",
                    "space_metrics": {
                        "total_units": "$total_units",
                        "total_value": {"$round": ["$total_value", 2]},
                        "product_count": "$product_count",
                        "avg_units_per_product": {
                            "$round": [
                                {"$divide": ["$total_units", "$product_count"]},
                                1
                            ]
                        },
                        "value_density": {
                            "$round": [
                                {"$divide": ["$total_value", "$total_units"]},
                                2
                            ]
                        }
                    },
                    "efficiency_score": {
                        "$round": [
                            {"$multiply": [
                                {"$divide": ["$total_value", "$total_units"]},
                                {"$sqrt": "$product_count"}
                            ]},
                            2
                        ]
                    },
                    "_id": 0
                }
            },
            {
                "$sort": {"efficiency_score": -1}
            }
        ]
    
    @staticmethod
    def stock_alert_dashboard() -> List[Dict[str, Any]]:
        """Comprehensive stock alert dashboard."""
        return [
            {
                "$addFields": {
                    "alert_level": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$stock", 0]}, "then": "critical"},
                                {"case": {"$lte": ["$stock", 3]}, "then": "high"},
                                {"case": {"$lte": ["$stock", settings.low_stock_threshold]}, "then": "medium"},
                                {"case": {"$gte": ["$stock", 100]}, "then": "overstocked"}
                            ],
                            "default": "normal"
                        }
                    },
                    "financial_impact": {"$multiply": ["$price", "$stock"]},
                    "action_priority": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$stock", 0]}, "then": 10},
                                {"case": {"$lte": ["$stock", 3]}, "then": 8},
                                {"case": {"$lte": ["$stock", settings.low_stock_threshold]}, "then": 5},
                                {"case": {"$gte": ["$stock", 100]}, "then": 3}
                            ],
                            "default": 1
                        }
                    }
                }
            },
            {
                "$match": {
                    "alert_level": {"$ne": "normal"}
                }
            },
            {
                "$project": {
                    "product_info": {
                        "name": "$name",
                        "sku": "$sku",
                        "category": "$category"
                    },
                    "stock_info": {
                        "current_stock": "$stock",
                        "alert_level": "$alert_level",
                        "price": "$price",
                        "financial_impact": {"$round": ["$financial_impact", 2]}
                    },
                    "recommendations": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {"$eq": ["$alert_level", "critical"]},
                                    "then": ["immediate_restock", "check_supplier", "notify_sales"]
                                },
                                {
                                    "case": {"$eq": ["$alert_level", "high"]},
                                    "then": ["schedule_restock", "contact_supplier"]
                                },
                                {
                                    "case": {"$eq": ["$alert_level", "medium"]},
                                    "then": ["plan_restock", "monitor_sales"]
                                },
                                {
                                    "case": {"$eq": ["$alert_level", "overstocked"]},
                                    "then": ["review_demand", "consider_promotion", "reduce_orders"]
                                }
                            ],
                            "default": ["monitor"]
                        }
                    },
                    "action_priority": 1
                }
            },
            {
                "$sort": {"action_priority": -1}
            }
        ] 