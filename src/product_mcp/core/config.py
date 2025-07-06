from typing import List, Optional, Dict, Union
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

class ServerConfig(TypedDict):
    host: str
    port: int
    transport: str

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI"
    )
    database_name: str = Field(
        default="product_management",
        description="Database name"
    )
    
    mcp_host: str = Field(
        default="0.0.0.0",
        description="MCP server host for remote deployment"
    )
    mcp_port: int = Field(
        default=8000,
        description="MCP server port for remote deployment"  
    )
    mcp_transport: str = Field(
        default="stdio",
        description="MCP transport type (stdio, sse, http)"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (optional)"
    )
    
    low_stock_threshold: int = Field(
        default=10,
        description="Threshold for low stock warnings"
    )
    default_currency: str = Field(
        default="USD",
        description="Default currency for prices"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        env_prefix = ""
        
        fields: Dict[str, Dict[str, Union[str, List[str]]]] = {
            "mongodb_uri": {"env": ["MONGODB_URI", "DATABASE_URL"]},
            "database_name": {"env": "DATABASE_NAME"},
            "mcp_host": {"env": "MCP_HOST"},
            "mcp_port": {"env": "MCP_PORT"},
            "mcp_transport": {"env": "MCP_TRANSPORT"},
            "log_level": {"env": "LOG_LEVEL"},
            "log_file": {"env": "LOG_FILE"},
            "low_stock_threshold": {"env": "LOW_STOCK_THRESHOLD"},
            "default_currency": {"env": "DEFAULT_CURRENCY"},
        }


settings = Settings()


def get_connection_string() -> str:
    """Get the complete MongoDB connection string."""
    return settings.mongodb_uri


def is_remote_mode() -> bool:
    """Check if running in remote mode (SSE/HTTP)."""
    return settings.mcp_transport.lower() in ("sse", "http", "streamable-http")


def get_server_config() -> ServerConfig:
    """Get server configuration for remote deployment."""
    return {
        "host": settings.mcp_host,
        "port": settings.mcp_port,
        "transport": settings.mcp_transport,
    }