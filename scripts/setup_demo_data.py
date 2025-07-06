import sys
import os
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from product_mcp.core.database import db_manager
from product_mcp.core.models import ProductCreate, ProductCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DEMO_PRODUCTS: List[Dict[str, Any]] = [
    {
        "name": "Wireless Noise-Canceling Headphones",
        "description": "Premium wireless headphones with active noise cancellation, 30-hour battery life, and studio-quality sound.",
        "price": 299.99,
        "stock": 45,
        "category": ProductCategory.ELECTRONICS,
        "sku": "ELEC-WH-001",
        "tags": ["wireless", "bluetooth", "noise-canceling", "premium", "audio"]
    },
    {
        "name": "Gaming Mechanical Keyboard",
        "description": "Professional gaming keyboard with RGB backlighting, Cherry MX switches, and programmable keys.",
        "price": 159.99,
        "stock": 23,
        "category": ProductCategory.ELECTRONICS,
        "sku": "ELEC-KB-001",
        "tags": ["gaming", "mechanical", "rgb", "keyboard", "professional"]
    },
    {
        "name": "4K Webcam with Auto Focus",
        "description": "Ultra HD webcam with auto focus, noise reduction, and wide-angle lens for professional streaming.",
        "price": 129.99,
        "stock": 67,
        "category": ProductCategory.ELECTRONICS,
        "sku": "ELEC-CAM-001",
        "tags": ["4k", "webcam", "streaming", "professional", "auto-focus"]
    },
    {
        "name": "Smartphone with 5G",
        "description": "Latest flagship smartphone with 5G connectivity, 108MP camera, and all-day battery life.",
        "price": 899.99,
        "stock": 12,
        "category": ProductCategory.ELECTRONICS,
        "sku": "ELEC-PHONE-001",
        "tags": ["smartphone", "5g", "camera", "flagship", "mobile"]
    },
    {
        "name": "Wireless Charging Pad",
        "description": "Fast wireless charging pad compatible with all Qi-enabled devices, sleek design.",
        "price": 39.99,
        "stock": 156,
        "category": ProductCategory.ELECTRONICS,
        "sku": "ELEC-CHRG-001",
        "tags": ["wireless", "charging", "qi", "fast-charge", "accessories"]
    },
    
    {
        "name": "Premium Cotton T-Shirt",
        "description": "100% organic cotton t-shirt with modern fit, available in multiple colors.",
        "price": 29.99,
        "stock": 234,
        "category": ProductCategory.CLOTHING,
        "sku": "CLO-TSHIRT-001",
        "tags": ["cotton", "organic", "casual", "comfortable", "basic"]
    },
    {
        "name": "Professional Dress Shirt",
        "description": "Wrinkle-resistant dress shirt perfect for business and formal occasions.",
        "price": 79.99,
        "stock": 89,
        "category": ProductCategory.CLOTHING,
        "sku": "CLO-DRESS-001",
        "tags": ["formal", "business", "wrinkle-resistant", "professional", "shirt"]
    },
    {
        "name": "Denim Jeans - Classic Fit",
        "description": "Premium denim jeans with classic fit, durable construction, and timeless style.",
        "price": 89.99,
        "stock": 76,
        "category": ProductCategory.CLOTHING,
        "sku": "CLO-JEANS-001",
        "tags": ["denim", "jeans", "classic", "durable", "casual"]
    },
    {
        "name": "Winter Jacket - Waterproof",
        "description": "Insulated winter jacket with waterproof exterior and breathable lining.",
        "price": 199.99,
        "stock": 34,
        "category": ProductCategory.CLOTHING,
        "sku": "CLO-JACKET-001",
        "tags": ["winter", "waterproof", "insulated", "outdoor", "jacket"]
    },
    {
        "name": "Running Shoes",
        "description": "Lightweight running shoes with advanced cushioning and breathable mesh upper.",
        "price": 129.99,
        "stock": 0,
        "category": ProductCategory.CLOTHING,
        "sku": "CLO-SHOES-001",
        "tags": ["running", "athletic", "lightweight", "cushioning", "sports"]
    },
    
    {
        "name": "Modern Software Architecture",
        "description": "Comprehensive guide to modern software architecture patterns and best practices.",
        "price": 59.99,
        "stock": 145,
        "category": ProductCategory.BOOKS,
        "sku": "BOOK-ARCH-001",
        "tags": ["software", "architecture", "programming", "technical", "guide"]
    },
    {
        "name": "Data Science with Python",
        "description": "Practical introduction to data science using Python, NumPy, and Pandas.",
        "price": 49.99,
        "stock": 223,
        "category": ProductCategory.BOOKS,
        "sku": "BOOK-DATA-001",
        "tags": ["data-science", "python", "analytics", "programming", "education"]
    },
    {
        "name": "Digital Marketing Mastery",
        "description": "Complete guide to digital marketing strategies for modern businesses.",
        "price": 39.99,
        "stock": 187,
        "category": ProductCategory.BOOKS,
        "sku": "BOOK-MARK-001",
        "tags": ["marketing", "digital", "business", "strategy", "online"]
    },
    {
        "name": "Investment Fundamentals",
        "description": "Essential guide to personal investing and financial planning.",
        "price": 34.99,
        "stock": 98,
        "category": ProductCategory.BOOKS,
        "sku": "BOOK-INV-001",
        "tags": ["investing", "finance", "personal", "money", "planning"]
    },
    
    {
        "name": "Smart Home Security Camera",
        "description": "WiFi-enabled security camera with motion detection, night vision, and mobile app.",
        "price": 179.99,
        "stock": 56,
        "category": ProductCategory.HOME,
        "sku": "HOME-CAM-001",
        "tags": ["smart-home", "security", "wifi", "surveillance", "mobile-app"]
    },
    {
        "name": "Coffee Maker with Grinder",
        "description": "All-in-one coffee maker with built-in grinder and programmable brewing.",
        "price": 249.99,
        "stock": 78,
        "category": ProductCategory.HOME,
        "sku": "HOME-COFFEE-001",
        "tags": ["coffee", "grinder", "programmable", "kitchen", "appliance"]
    },
    {
        "name": "Ergonomic Office Chair",
        "description": "Professional office chair with lumbar support, adjustable height, and breathable mesh.",
        "price": 399.99,
        "stock": 23,
        "category": ProductCategory.HOME,
        "sku": "HOME-CHAIR-001",
        "tags": ["office", "ergonomic", "chair", "professional", "comfortable"]
    },
    {
        "name": "LED Desk Lamp",
        "description": "Adjustable LED desk lamp with multiple brightness levels and USB charging port.",
        "price": 89.99,
        "stock": 134,
        "category": ProductCategory.HOME,
        "sku": "HOME-LAMP-001",
        "tags": ["led", "desk", "lamp", "adjustable", "usb-charging"]
    },
    
    {
        "name": "Yoga Mat - Premium",
        "description": "Non-slip yoga mat with extra cushioning and carrying strap.",
        "price": 49.99,
        "stock": 267,
        "category": ProductCategory.SPORTS,
        "sku": "SPORT-YOGA-001",
        "tags": ["yoga", "fitness", "mat", "non-slip", "exercise"]
    },
    {
        "name": "Resistance Band Set",
        "description": "Complete resistance band set with multiple resistance levels and door anchor.",
        "price": 29.99,
        "stock": 189,
        "category": ProductCategory.SPORTS,
        "sku": "SPORT-BAND-001",
        "tags": ["resistance", "bands", "fitness", "home-gym", "strength"]
    },
    {
        "name": "Smart Fitness Tracker",
        "description": "Advanced fitness tracker with heart rate monitoring, GPS, and smartphone notifications.",
        "price": 199.99,
        "stock": 45,
        "category": ProductCategory.SPORTS,
        "sku": "SPORT-TRACK-001",
        "tags": ["fitness", "tracker", "smart", "gps", "health"]
    },
    {
        "name": "Protein Powder - Vanilla",
        "description": "Premium whey protein powder with 25g protein per serving, vanilla flavor.",
        "price": 39.99,
        "stock": 156,
        "category": ProductCategory.HEALTH,
        "sku": "HEALTH-PROT-001",
        "tags": ["protein", "whey", "vanilla", "nutrition", "fitness"]
    },
    
    {
        "name": "Car Phone Mount",
        "description": "Universal car phone mount with 360-degree rotation and secure grip.",
        "price": 24.99,
        "stock": 345,
        "category": ProductCategory.AUTOMOTIVE,
        "sku": "AUTO-MOUNT-001",
        "tags": ["car", "phone", "mount", "universal", "accessories"]
    },
    {
        "name": "Dash Camera with GPS",
        "description": "HD dash camera with GPS tracking, night vision, and loop recording.",
        "price": 149.99,
        "stock": 67,
        "category": ProductCategory.AUTOMOTIVE,
        "sku": "AUTO-DASH-001",
        "tags": ["dash-cam", "gps", "hd", "night-vision", "safety"]
    },
    {
        "name": "Car Emergency Kit",
        "description": "Complete emergency kit with jumper cables, flashlight, and first aid supplies.",
        "price": 79.99,
        "stock": 89,
        "category": ProductCategory.AUTOMOTIVE,
        "sku": "AUTO-EMERG-001",
        "tags": ["emergency", "safety", "jumper-cables", "first-aid", "car"]
    }
]


def create_demo_products() -> None:
    """Create demo products in the database."""
    logger.info("Starting demo data creation...")
    
    created_count = 0
    skipped_count = 0
    
    for product_data in DEMO_PRODUCTS:
        try:
            existing = db_manager.get_product_by_sku(str(product_data["sku"]))
            if existing:
                logger.info(f"Product with SKU {product_data['sku']} already exists, skipping...")
                skipped_count += 1
                continue
            
            product_create = ProductCreate(**product_data)
            created_product = db_manager.create_product(product_create)
            
            if created_product:
                logger.info(f"Created product: {created_product.name} (SKU: {created_product.sku})")
                created_count += 1
            else:
                logger.error(f"Failed to create product: {product_data['name']}")
                
        except Exception as e:
            logger.error(f"Error creating product {product_data['name']}: {e}")
    
    logger.info(f"Demo data creation completed!")
    logger.info(f"Products created: {created_count}")
    logger.info(f"Products skipped: {skipped_count}")
    logger.info(f"Total products in demo data: {len(DEMO_PRODUCTS)}")


def verify_demo_data() -> None:
    """Verify that demo data was created successfully."""
    logger.info("Verifying demo data...")
    
    try:
        summary = db_manager.get_inventory_summary()
        
        logger.info(f"Total products in database: {summary.total_products}")
        logger.info(f"Total inventory value: ${summary.total_value:,.2f}")
        logger.info(f"Categories in use: {len(summary.categories_breakdown)}")
        
        logger.info("Category breakdown:")
        for category in summary.categories_breakdown:
            logger.info(f"  - {category['_id']}: {category['count']} products, ${category['total_value']:,.2f}")
        
        logger.info(f"Low stock products: {summary.low_stock_products}")
        logger.info(f"Out of stock products: {summary.out_of_stock_products}")
        
        logger.info("Demo data verification completed successfully!")
        
    except Exception as e:
        logger.error(f"Error verifying demo data: {e}")


def main() -> None:
    """Main function to set up demo data."""
    try:
        health = db_manager.health_check()
        if not health['connected']:
            logger.error(f"Database connection failed: {health.get('error')}")
            sys.exit(1)
        
        logger.info(f"Connected to database: {health['database']}")
        
        create_demo_products()
        
        verify_demo_data()
        
        logger.info("Setup completed successfully!")
        logger.info("You can now run the MCP server and explore the demo data.")
        
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
    except Exception as e:
        logger.error(f"Setup error: {e}")
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == "__main__":
    main() 