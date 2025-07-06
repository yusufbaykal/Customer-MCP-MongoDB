import logging
import sys
from typing import Dict, Any
from fastmcp import FastMCP

from .core.config import settings
from .core.database import db_manager
from .tools.product_tools import ProductTools
from .tools.analytics_tools import AnalyticsTools  
from .tools.inventory_tools import InventoryTools
from .prompts import PromptRegistry

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=settings.log_file if settings.log_file else None
)
logger = logging.getLogger(__name__)

mcp = FastMCP(  # type: ignore[type-arg]
    name="product-mcp-server",
    version="1.0.0"
)


@mcp.resource("database://status")
def database_status() -> str:
    """Get database connection status and health metrics."""
    try:
        health_data: Dict[str, Any] = db_manager.health_check()
        
        status_info = f"""# Database Status

        **Connection**: {'✅ Connected' if health_data['connected'] else '❌ Disconnected'}
        **Database**: {health_data.get('database', 'Unknown')}
        **Total Products**: {health_data.get('total_products', 0)}

        ## Storage Metrics
        - **Database Size**: {health_data.get('database_size', 0):,} bytes
        - **Collection Size**: {health_data.get('collection_size', 0):,} bytes  
        - **Index Count**: {health_data.get('index_count', 0)}

        ## Health Check
        - **Status**: {health_data['status'].title()}
        - **Last Check**: {health_data['last_check']}
        """
        if not health_data['connected']:
            status_info += f"\n**Error**: {health_data.get('error', 'Unknown error')}"
            
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return f"""# Database Status

        ❌ **Error**: Failed to retrieve database status
        **Details**: {str(e)}
        """


@mcp.resource("database://schema")
def database_schema() -> str:
    """Get database schema information."""
    return """# Database Schema

        ## Collections

        ### products
        Main product collection with the following fields:

        - **_id**: ObjectId (Primary key)
        - **name**: String (Product name, indexed for text search)
        - **description**: String (Optional product description)
        - **price**: Number (Product price, must be positive)
        - **stock**: Number (Stock quantity, non-negative)
        - **category**: String (Product category, indexed)
        - **status**: String (Product status, indexed)
        - **sku**: String (Unique product identifier, unique index)
        - **tags**: Array[String] (Search tags, text indexed)
        - **created_at**: Date (Creation timestamp, indexed)
        - **updated_at**: Date (Last update timestamp, indexed)

        ## Indexes

        1. **sku_unique**: Unique index on SKU field
        2. **text_search**: Text index on name, description, tags
        3. **category_idx**: Index on category field
        4. **status_idx**: Index on status field
        5. **price_idx**: Index on price field
        6. **stock_idx**: Index on stock field
        7. **category_status_stock_idx**: Compound index for common queries
        8. **created_at_idx**: Index on creation date
        9. **updated_at_idx**: Index on update date
        """


@mcp.resource("templates://product")
def product_templates() -> str:
    """Get product creation templates for different categories."""
    return """# Product Templates

        ## Electronics Template
        ```json
        {
        "name": "Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 199.99,
        "stock": 50,
        "category": "electronics",
        "sku": "ELEC-WH-001",
        "tags": ["wireless", "audio", "electronics", "bluetooth"]
        }
        ```

        ## Clothing Template
        ```json
        {
        "name": "Cotton T-Shirt",
        "description": "Comfortable 100% cotton t-shirt",
        "price": 29.99,
        "stock": 100,
        "category": "clothing",
        "sku": "CLO-TS-001",
        "tags": ["cotton", "apparel", "casual", "comfortable"]
        }
        ```

        ## Books Template
        ```json
        {
        "name": "Programming Guide",
        "description": "Comprehensive programming tutorial",
        "price": 49.99,
        "stock": 25,
        "category": "books",
        "sku": "BOOK-PROG-001",
        "tags": ["programming", "tutorial", "education", "technology"]
        }
        ```

        Use these templates as starting points for creating new products.
        Adjust the values according to your specific product requirements.
        """


def register_all_tools() -> None:
    """Register all tools from different modules."""
    try:
        ProductTools.register_tools(mcp)  # type: ignore[arg-type]
        logger.info("Product tools registered successfully")
        
        AnalyticsTools.register_tools(mcp)  # type: ignore[arg-type]
        logger.info("Analytics tools registered successfully")
        
        InventoryTools.register_tools(mcp)  # type: ignore[arg-type]
        logger.info("Inventory tools registered successfully")
        
    except Exception as e:
        logger.error(f"Error registering tools: {e}")
        raise


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        health: Dict[str, Any] = db_manager.health_check()
        if not health['connected']:
            logger.error(f"Database connection failed: {health.get('error')}")
            sys.exit(1)
        
        logger.info(f"Database connected successfully: {health['database']}")
        register_all_tools()
        PromptRegistry.register_prompts(mcp)  # type: ignore[arg-type]
        
        logger.info("Starting Product MCP Server (stdio transport)")
        
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        db_manager.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    main() 