import logging
import sys
import uvicorn
from typing import Any
from starlette.requests import Request

from fastmcp import FastMCP

from .core.config import settings, get_server_config
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
    name="product-mcp-server-remote",
    version="1.0.0"
)


@mcp.resource("database://status")
def database_status() -> str:
    """Get database connection status and health metrics."""
    try:
        health_data: dict[str, Any] = db_manager.health_check()
        
        status_info = f"""# Database Status (Remote)

**Connection**: {'✅ Connected' if health_data['connected'] else '❌ Disconnected'}
**Database**: {health_data.get('database', 'Unknown')}
**Total Products**: {health_data.get('total_products', 0)}
**Server Mode**: Remote (SSE/HTTP)

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
        return f"""# Database Status (Remote)

❌ **Error**: Failed to retrieve database status
**Details**: {str(e)}
"""


@mcp.resource("server://config")
def server_config() -> str:
    """Get remote server configuration information."""
    config = get_server_config()
    
    return f"""# Remote Server Configuration

**Host**: {config['host']}
**Port**: {config['port']}
**Transport**: {config['transport']}
**Environment**: {'Production' if settings.mcp_host != '0.0.0.0' else 'Development'}

## Endpoints
- **SSE Endpoint**: http://{config['host']}:{config['port']}/sse
- **Health Check**: http://{config['host']}:{config['port']}/health
- **Metrics**: http://{config['host']}:{config['port']}/metrics

## Connection Examples

### Claude Desktop (Remote)
```json
{{
  "mcpServers": {{
    "product-manager": {{
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-sse",
        "http://{config['host']}:{config['port']}/sse"
      ]
    }}
  }}
}}
```

### Direct HTTP Client
```bash
curl -X POST http://{config['host']}:{config['port']}/tools/search_products \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "electronics"}}'
```
"""


@mcp.resource("api://endpoints")
def api_endpoints() -> str:
    """List all available API endpoints and their usage."""
    return """# API Endpoints Reference

## Tools Endpoints
All tools are available via POST requests to `/tools/{tool_name}`

### Product Management
- `POST /tools/create_product` - Create new product
- `POST /tools/get_product` - Retrieve product by ID/SKU
- `POST /tools/search_products` - Search products with filters
- `POST /tools/update_product` - Update product information
- `POST /tools/delete_product` - Delete product (requires confirmation)

### Analytics
- `POST /tools/get_sales_analytics` - Sales performance metrics
- `POST /tools/get_category_analytics` - Category analysis
- `POST /tools/get_price_analysis` - Price distribution analysis
- `POST /tools/get_trending_products` - Trending products analysis
- `POST /tools/get_inventory_velocity` - Inventory turnover metrics
- `POST /tools/generate_executive_summary` - Executive dashboard

### Inventory Management
- `POST /tools/get_inventory_summary` - Complete inventory overview
- `POST /tools/check_low_stock` - Low stock alerts
- `POST /tools/update_stock` - Update stock levels
- `POST /tools/get_stock_distribution` - Stock distribution analysis
- `POST /tools/analyze_inventory_turnover` - Turnover analysis
- `POST /tools/get_stock_alerts_dashboard` - Alerts dashboard

## Resources Endpoints
- `GET /resources/database://status` - Database health status
- `GET /resources/database://schema` - Database schema info
- `GET /resources/server://config` - Server configuration
- `GET /resources/api://endpoints` - This endpoint list
- `GET /resources/templates://product` - Product templates

## System Endpoints
- `GET /health` - Server health check
- `GET /metrics` - Server metrics (if enabled)
- `GET /sse` - Server-Sent Events endpoint for MCP clients
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


def create_sse_app():
    """Create Starlette app using FastMCP's sse_app helper."""
    app = mcp.sse_app(path="/sse")

    @app.route("/health", methods=["GET"])  # type: ignore[misc]
    async def health_check(request: Request) -> dict[str, Any]:  # type: ignore[misc]
        health_data: dict[str, Any] = db_manager.health_check()
        return {
            "status": "healthy" if health_data["connected"] else "unhealthy",
            "database": health_data,
            "server": "product-mcp-server-remote"
        }

    @app.route("/metrics", methods=["GET"])  # type: ignore[misc]
    async def metrics(request: Request) -> dict[str, Any]:  # type: ignore[misc]
        inventory_summary = db_manager.get_inventory_summary()
        return {
            "products": {
                "total": inventory_summary.total_products,
                "total_value": inventory_summary.total_value,
            },
            "categories": len(inventory_summary.categories_breakdown),
            "last_updated": inventory_summary.last_updated.isoformat()
        }

    return app


def main() -> None:
    """Main entry point for the remote MCP server."""
    try:
        health: dict[str, Any] = db_manager.health_check()
        if not health['connected']:
            logger.error(f"Database connection failed: {health.get('error')}")
            sys.exit(1)
        
        logger.info(f"Database connected successfully: {health['database']}")
        
        register_all_tools()
        PromptRegistry.register_prompts(mcp)  # type: ignore[arg-type]
        
        server_config = get_server_config()
        
        logger.info(f"Starting Product MCP Server (Remote)")
        logger.info(f"Transport: {server_config['transport']}")
        logger.info(f"Host: {server_config['host']}")
        logger.info(f"Port: {server_config['port']}")
        
        if settings.mcp_transport.lower() == "fastapi":
            app = create_sse_app()
            uvicorn.run(app, host=server_config['host'], port=server_config['port'], log_level=settings.log_level.lower())
        else:
            # Type ignore needed due to FastMCP transport type constraints
            mcp.run(  # type: ignore[arg-type]
                transport=server_config['transport'],  # type: ignore[arg-type]
                host=server_config['host'],
                port=server_config['port']
            )
        
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