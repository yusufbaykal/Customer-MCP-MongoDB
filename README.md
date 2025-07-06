# Product MCP Server
A Model Context Protocol (MCP) server that provides comprehensive product management capabilities, allowing AI assistants to interact with your product database for inventory management, analytics, and business intelligence.

![product-mcp](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDh3NjlxdHB5Zjd3bnZ6Nmhxemhzc2E3YXR1M2sxbzU3ZHJ3cnBibSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/EeG8Wo0dz3q31ww2JU/giphy.gif)

## Overview
This MCP server connects to your MongoDB database and exposes various tools to manage products, track inventory, analyze sales data, and generate business insights. It's designed to work with MCP-compatible AI assistants like Claude Desktop, enabling natural language interactions with your complete product management system.

This server demonstrates professional MCP server development patterns using modern Python technologies, FastMCP framework, and MongoDB aggregation pipelines for advanced analytics and business intelligence.

## Prerequisites
* MongoDB database (local or remote)
* Python 3.10 or higher
* Access to your MongoDB database

## Installation

### Option 1: Local Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yusufbaykal/Customer-MCP-MongoDB.git
   cd Customer-MCP-MongoDB
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set environment variables (optional):**
   ```bash
   # Set environment variables directly
   export MONGODB_URI="mongodb://localhost:27017"
   export DATABASE_NAME="product_management"
   export MCP_HOST="0.0.0.0"
   export MCP_PORT="8000"
   ```

4. **Load demo data (recommended for first-time setup):**
   ```bash
   python scripts/setup_demo_data.py
   ```
   
   This script will populate your database with sample products, customers, and orders to help you get started quickly.

### Option 2: Quick Start

For quick testing and development, you can run the server directly:

```bash
# Clone and navigate to the repository
git clone https://github.com/yusufbaykal/Customer-MCP-MongoDB.git
cd Customer-MCP-MongoDB

# Install dependencies
pip install -e .

# Load demo data (recommended)
python scripts/setup_demo_data.py

# Run the server directly
python -m product_mcp.server
```

## Available Tools

The MCP server provides **17 tools** organized into three main categories:

### Product Management Tools

1. `create_product` - Create new products with comprehensive validation
2. `get_product` - Retrieve product by ID or SKU with full details
3. `search_products` - Advanced product search with filters and pagination
4. `update_product` - Update product information with validation
5. `delete_product` - Remove products with confirmation safeguards

### Analytics & Business Intelligence Tools

6. `get_sales_analytics` - Sales performance metrics and trends analysis
7. `get_category_analytics` - Category-wise performance breakdown
8. `get_price_analysis` - Pricing strategy insights and recommendations
9. `get_trending_products` - Product popularity and trend analysis
10. `get_inventory_velocity` - Inventory velocity analysis
11. `generate_executive_summary` - High-level business dashboard and KPIs

### Inventory Management Tools

12. `get_inventory_summary` - Complete inventory overview with health metrics
13. `check_low_stock` - Low stock alerts with reorder recommendations
14. `update_stock` - Stock level modifications with change tracking
15. `get_stock_distribution` - Stock distribution analysis by category
16. `analyze_inventory_turnover` - Inventory velocity and turnover metrics
17. `get_stock_alerts_dashboard` - Comprehensive stock alert system

## Configuration

### Environment Variables

The following environment variables can be set to configure the server:

```env
# Database Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=product_management

# MCP Server Configuration (for remote deployment)
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_TRANSPORT=sse

# Optional Configuration
LOW_STOCK_THRESHOLD=10
DEFAULT_CURRENCY=USD
LOG_LEVEL=INFO
LOG_FILE=product_mcp.log
```

**Note**: Set these variables as environment variables directly or create a .env file in your project root.

Example .env file:
```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=product_management
LOG_LEVEL=INFO
```

### MCP Client Configuration

To use this server with Claude Desktop, add the following to your MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Local Configuration (stdio transport)

**Important**: Replace `/path/to/your/project` with your actual project path.

```json
{
  "mcpServers": {
    "product-manager": {
      "command": "python3",
      "args": ["-m", "product_mcp.server"],
      "cwd": "/path/to/your/project/Customer-MCP-MongoDB",
      "env": {
        "PYTHONPATH": "/path/to/your/project/Customer-MCP-MongoDB/src",
        "MONGODB_URI": "mongodb://localhost:27017",
        "DATABASE_NAME": "product_management",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Example for macOS**:
```json
{
  "mcpServers": {
    "product-manager": {
      "command": "python3",
      "args": ["-m", "product_mcp.server"],
      "cwd": "/Users/yourusername/Desktop/Customer-MCP-MongoDB",
      "env": {
        "PYTHONPATH": "/Users/yourusername/Desktop/Customer-MCP-MongoDB/src",
        "MONGODB_URI": "mongodb://localhost:27017",
        "DATABASE_NAME": "product_management",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Example for Windows**:
```json
{
  "mcpServers": {
    "product-manager": {
      "command": "python",
      "args": ["-m", "product_mcp.server"],
      "cwd": "C:\\Users\\yourusername\\Desktop\\Customer-MCP-MongoDB",
      "env": {
        "PYTHONPATH": "C:\\Users\\yourusername\\Desktop\\Customer-MCP-MongoDB\\src",
        "MONGODB_URI": "mongodb://localhost:27017",
        "DATABASE_NAME": "product_management",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Remote Configuration (SSE transport)

For connecting to a remote server:

```json
{
  "mcpServers": {
    "product-manager": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-sse",
        "http://your-server:8000/sse"
      ]
    }
  }
}
```

## Usage

### Running the Server

#### Local Development (STDIO)
```bash
# Using package command
product-mcp

# Or directly with Python
python -m product_mcp.server
```

#### Remote Server (SSE/HTTP)
```bash
# Using package command
product-mcp-remote --host 0.0.0.0 --port 8000

# Or with environment variables
MCP_HOST=0.0.0.0 MCP_PORT=8000 python -m product_mcp.remote_server

# Test the server
curl http://localhost:8000/health
```

### Example Queries

Once configured with an MCP client, you can ask natural language questions:

#### Product Operations
* "Create a new wireless headphone product priced at $199.99"
* "Search for electronics products under $100"
* "Update the stock for product SKU WH-001 to 25 units"
* "Show me all products in the clothing category"

#### Analytics & Insights
* "What are my top selling products this month?"
* "Show me sales analytics by category"
* "Which products have the highest profit margins?"
* "Generate an executive summary of business performance"

#### Inventory Management
* "Which products are running low on stock?"
* "Show me inventory turnover analysis"
* "What's the total value of my inventory?"
* "Alert me about products that need restocking"

## Database Schema

The server automatically creates and manages these MongoDB collections:

### Products Collection
```javascript
{
  _id: ObjectId,
  name: String,           // Product name (indexed for search)
  description: String,    // Product description
  price: Number,          // Product price (positive)
  stock: Number,          // Current stock quantity
  category: String,       // Product category (indexed)
  status: String,         // Product status (indexed)
  sku: String,           // Unique identifier (unique index)
  tags: [String],        // Search tags (text indexed)
  created_at: Date,      // Creation timestamp
  updated_at: Date       // Last update timestamp
}
```

### Indexes
- `sku_unique` - Unique index on SKU field
- `text_search` - Text index on name, description, tags
- `category_status_stock_idx` - Compound index for common queries
- Individual indexes on category, status, price, stock fields

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
black src/
isort src/

# Run type checking
mypy src/
```

### Project Structure

```
src/product_mcp/
├── __init__.py
├── server.py              # Main MCP server (stdio)
├── remote_server.py       # Remote MCP server (SSE/HTTP)  
├── prompts.py             # MCP prompt templates
├── core/
│   ├── __init__.py
│   ├── database.py        # MongoDB operations & health checks
│   ├── models.py          # Pydantic data models
│   └── config.py          # Configuration management
├── queries/
│   ├── __init__.py
│   ├── analytics.py       # Analytics aggregation templates
│   ├── inventory.py       # Inventory query templates
│   └── reports.py         # Reporting aggregations
└── tools/
    ├── __init__.py
    ├── product_tools.py   # Product CRUD operations
    ├── analytics_tools.py # Analytics & reporting tools
    └── inventory_tools.py # Inventory management tools
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [FastMCP](https://github.com/jlowin/fastmcp) - High-level MCP server framework
* [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol specification
* [MongoDB](https://www.mongodb.com/) - NoSQL database platform
* [Pydantic](https://pydantic.dev/) - Data validation and settings management
