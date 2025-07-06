from datetime import datetime, timedelta
from typing import Dict, List, Any


class ReportsQueries:
    """Template-based reporting queries for business intelligence."""
    
    @staticmethod
    def executive_dashboard_summary() -> List[Dict[str, Any]]:
        """Executive dashboard with key business metrics."""
        return [
            {
                "$facet": {
                    "overall_metrics": [
                        {
                            "$group": {
                                "_id": None,
                                "total_products": {"$sum": 1},
                                "total_inventory_value": {"$sum": {"$multiply": ["$price", "$stock"]}},
                                "avg_product_price": {"$avg": "$price"},
                                "total_stock_units": {"$sum": "$stock"}
                            }
                        }
                    ],
                    "category_breakdown": [
                        {
                            "$group": {
                                "_id": "$category",
                                "count": {"$sum": 1},
                                "value": {"$sum": {"$multiply": ["$price", "$stock"]}}
                            }
                        },
                        {"$sort": {"value": -1}}
                    ],
                    "status_breakdown": [
                        {
                            "$group": {
                                "_id": "$status",
                                "count": {"$sum": 1},
                                "value": {"$sum": {"$multiply": ["$price", "$stock"]}}
                            }
                        }
                    ],
                    "alerts": [
                        {
                            "$match": {
                                "$or": [
                                    {"stock": 0},
                                    {"stock": {"$lte": 10}}
                                ]
                            }
                        },
                        {
                            "$project": {
                                "name": 1,
                                "sku": 1,
                                "stock": 1,
                                "alert_type": {
                                    "$cond": [
                                        {"$eq": ["$stock", 0]},
                                        "out_of_stock",
                                        "low_stock"
                                    ]
                                }
                            }
                        },
                        {"$limit": 10}
                    ]
                }
            }
        ]
    
    @staticmethod
    def financial_performance_report(days: int = 30) -> List[Dict[str, Any]]:
        """Financial performance report with trends."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return [
            {
                "$addFields": {
                    "is_recent": {"$gte": ["$created_at", cutoff_date]},
                    "inventory_value": {"$multiply": ["$price", "$stock"]}
                }
            },
            {
                "$facet": {
                    "current_period": [
                        {
                            "$group": {
                                "_id": None,
                                "total_value": {"$sum": "$inventory_value"},
                                "new_products_value": {
                                    "$sum": {
                                        "$cond": ["$is_recent", "$inventory_value", 0]
                                    }
                                },
                                "avg_price": {"$avg": "$price"},
                                "price_distribution": {
                                    "$push": {
                                        "category": "$category",
                                        "price": "$price",
                                        "value": "$inventory_value"
                                    }
                                }
                            }
                        }
                    ],
                    "category_financials": [
                        {
                            "$group": {
                                "_id": "$category",
                                "total_value": {"$sum": "$inventory_value"},
                                "avg_price": {"$avg": "$price"},
                                "product_count": {"$sum": 1},
                                "new_products": {
                                    "$sum": {"$cond": ["$is_recent", 1, 0]}
                                }
                            }
                        },
                        {
                            "$project": {
                                "category": "$_id",
                                "financial_metrics": {
                                    "total_value": {"$round": ["$total_value", 2]},
                                    "avg_price": {"$round": ["$avg_price", 2]},
                                    "product_count": "$product_count",
                                    "value_per_product": {
                                        "$round": [
                                            {"$divide": ["$total_value", "$product_count"]},
                                            2
                                        ]
                                    }
                                },
                                "growth_indicators": {
                                    "new_products": "$new_products",
                                    "growth_rate": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": ["$new_products", "$product_count"]},
                                                100
                                            ]},
                                            1
                                        ]
                                    }
                                },
                                "_id": 0
                            }
                        },
                        {"$sort": {"financial_metrics.total_value": -1}}
                    ],
                    "price_segments": [
                        {
                            "$bucket": {
                                "groupBy": "$price",
                                "boundaries": [0, 50, 100, 200, 500, 1000, float('inf')],
                                "default": "other",
                                "output": {
                                    "count": {"$sum": 1},
                                    "total_value": {"$sum": "$inventory_value"},
                                    "avg_stock": {"$avg": "$stock"}
                                }
                            }
                        }
                    ]
                }
            }
        ]
    
    @staticmethod
    def operational_efficiency_report() -> List[Dict[str, Any]]:
        """Operational efficiency metrics and KPIs."""
        return [
            {
                "$addFields": {
                    "stock_efficiency": {
                        "$cond": [
                            {"$eq": ["$stock", 0]},
                            0,
                            {"$divide": [{"$multiply": ["$price", "$stock"]}, "$stock"]}
                        ]
                    },
                    "category_value_density": {"$multiply": ["$price", "$stock"]},
                    "sku_efficiency": {"$strLenCP": "$sku"}
                }
            },
            {
                "$facet": {
                    "inventory_efficiency": [
                        {
                            "$group": {
                                "_id": "$category",
                                "avg_stock_efficiency": {"$avg": "$stock_efficiency"},
                                "total_products": {"$sum": 1},
                                "zero_stock_count": {
                                    "$sum": {"$cond": [{"$eq": ["$stock", 0]}, 1, 0]}
                                },
                                "high_value_count": {
                                    "$sum": {"$cond": [{"$gt": ["$price", 200]}, 1, 0]}
                                }
                            }
                        },
                        {
                            "$project": {
                                "category": "$_id",
                                "efficiency_metrics": {
                                    "stock_efficiency": {"$round": ["$avg_stock_efficiency", 2]},
                                    "availability_rate": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": [
                                                    {"$subtract": ["$total_products", "$zero_stock_count"]},
                                                    "$total_products"
                                                ]},
                                                100
                                            ]},
                                            1
                                        ]
                                    },
                                    "premium_product_ratio": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": ["$high_value_count", "$total_products"]},
                                                100
                                            ]},
                                            1
                                        ]
                                    }
                                },
                                "_id": 0
                            }
                        },
                        {"$sort": {"efficiency_metrics.stock_efficiency": -1}}
                    ],
                    "sku_management": [
                        {
                            "$group": {
                                "_id": None,
                                "avg_sku_length": {"$avg": "$sku_efficiency"},
                                "total_skus": {"$sum": 1},
                                "unique_skus": {"$addToSet": "$sku"}
                            }
                        },
                        {
                            "$project": {
                                "sku_metrics": {
                                    "avg_sku_length": {"$round": ["$avg_sku_length", 1]},
                                    "total_skus": "$total_skus",
                                    "unique_sku_count": {"$size": "$unique_skus"},
                                    "sku_uniqueness": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": [
                                                    {"$size": "$unique_skus"},
                                                    "$total_skus"
                                                ]},
                                                100
                                            ]},
                                            2
                                        ]
                                    }
                                },
                                "_id": 0
                            }
                        }
                    ],
                    "category_distribution": [
                        {
                            "$group": {
                                "_id": "$category",
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$group": {
                                "_id": None,
                                "categories": {
                                    "$push": {
                                        "category": "$_id",
                                        "count": "$count"
                                    }
                                },
                                "total": {"$sum": "$count"}
                            }
                        },
                        {
                            "$project": {
                                "distribution_metrics": {
                                    "$map": {
                                        "input": "$categories",
                                        "as": "cat",
                                        "in": {
                                            "category": "$$cat.category",
                                            "count": "$$cat.count",
                                            "percentage": {
                                                "$round": [
                                                    {"$multiply": [
                                                        {"$divide": ["$$cat.count", "$total"]},
                                                        100
                                                    ]},
                                                    1
                                                ]
                                            }
                                        }
                                    }
                                },
                                "_id": 0
                            }
                        }
                    ]
                }
            }
        ]
    
    @staticmethod
    def compliance_audit_report() -> List[Dict[str, Any]]:
        """Data quality and compliance audit report."""
        return [
            {
                "$addFields": {
                    "has_description": {"$ne": ["$description", None]},
                    "has_tags": {"$gt": [{"$size": "$tags"}, 0]},
                    "sku_valid": {
                        "$regexMatch": {
                            "input": "$sku",
                            "regex": "^[A-Z0-9_-]+$"
                        }
                    },
                    "price_reasonable": {
                        "$and": [
                            {"$gt": ["$price", 0]},
                            {"$lt": ["$price", 10000]}
                        ]
                    }
                }
            },
            {
                "$facet": {
                    "data_quality": [
                        {
                            "$group": {
                                "_id": None,
                                "total_products": {"$sum": 1},
                                "with_description": {"$sum": {"$cond": ["$has_description", 1, 0]}},
                                "with_tags": {"$sum": {"$cond": ["$has_tags", 1, 0]}},
                                "valid_skus": {"$sum": {"$cond": ["$sku_valid", 1, 0]}},
                                "reasonable_prices": {"$sum": {"$cond": ["$price_reasonable", 1, 0]}}
                            }
                        },
                        {
                            "$project": {
                                "quality_metrics": {
                                    "description_coverage": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": ["$with_description", "$total_products"]},
                                                100
                                            ]},
                                            1
                                        ]
                                    },
                                    "tag_coverage": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": ["$with_tags", "$total_products"]},
                                                100
                                            ]},
                                            1
                                        ]
                                    },
                                    "sku_compliance": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": ["$valid_skus", "$total_products"]},
                                                100
                                            ]},
                                            1
                                        ]
                                    },
                                    "price_validity": {
                                        "$round": [
                                            {"$multiply": [
                                                {"$divide": ["$reasonable_prices", "$total_products"]},
                                                100
                                            ]},
                                            1
                                        ]
                                    }
                                },
                                "_id": 0
                            }
                        }
                    ],
                    "compliance_issues": [
                        {
                            "$match": {
                                "$or": [
                                    {"has_description": False},
                                    {"has_tags": False},
                                    {"sku_valid": False},
                                    {"price_reasonable": False}
                                ]
                            }
                        },
                        {
                            "$project": {
                                "product": {
                                    "name": "$name",
                                    "sku": "$sku",
                                    "category": "$category"
                                },
                                "issues": {
                                    "$filter": {
                                        "input": [
                                            {"type": "missing_description", "has_issue": {"$not": "$has_description"}},
                                            {"type": "missing_tags", "has_issue": {"$not": "$has_tags"}},
                                            {"type": "invalid_sku", "has_issue": {"$not": "$sku_valid"}},
                                            {"type": "unreasonable_price", "has_issue": {"$not": "$price_reasonable"}}
                                        ],
                                        "cond": "$$this.has_issue"
                                    }
                                }
                            }
                        },
                        {"$limit": 50}
                    ]
                }
            }
        ] 