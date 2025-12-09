#!/usr/bin/env python
"""
Initialize database: create tables, admin user, and seed products
Run in Render 'release' phase
"""
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize everything"""
    logger.info("=" * 70)
    logger.info("DATABASE INITIALIZATION")
    logger.info("=" * 70)
    
    try:
        # Import Flask
        logger.info("\n[1/4] Importing Flask app...")
        from app import app, db
        from models import User, Item
        from werkzeug.security import generate_password_hash
        logger.info("OK Flask app imported")
        
        with app.app_context():
            # Step 1: Recreate tables
            logger.info("\n[2/4] Recreating database...")
            try:
                db.drop_all()
                logger.info("OK Tables dropped")
            except Exception as e:
                logger.warning("Warning dropping tables: {}".format(e))
            
            db.create_all()
            logger.info("OK Tables created")
            
            # Step 2: Create admin user
            logger.info("\n[3/4] Creating admin user...")
            admin = User.query.filter_by(username='admin').first()
            if admin:
                logger.info("OK Admin user exists")
            else:
                admin = User(
                    username='admin',
                    email='admin@sistema.local',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                logger.info("OK Admin user created (admin/admin123)")
            
            # Step 3: Seed products
            logger.info("\n[4/4] Adding products...")
            existing = Item.query.first()
            if existing:
                count = Item.query.count()
                logger.info("OK Database has {} products".format(count))
            else:
                try:
                    from seed_products import PRODUCTS
                    logger.info("OK Imported products from seed_products.py")
                    
                    total = 0
                    for category, products in PRODUCTS.items():
                        logger.info("  [{}]".format(category))
                        for product in products:
                            item = Item(
                                name=product['name'],
                                description=product.get('description', ''),
                                category=category,
                                price=product['price'],
                                stock=product['stock'],
                                rentable=product['rentable']
                            )
                            db.session.add(item)
                            total += 1
                    
                    db.session.commit()
                    logger.info("OK {} products added".format(total))
                    
                except ImportError as e:
                    logger.warning("WARNING: Could not import PRODUCTS: {}".format(e))
                except Exception as e:
                    logger.error("ERROR adding products: {}".format(e))
                    import traceback
                    traceback.print_exc()
        
        logger.info("\n" + "=" * 70)
        logger.info("OK INITIALIZATION COMPLETED")
        logger.info("=" * 70)
        return True
        
    except Exception as e:
        logger.error("CRITICAL ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
