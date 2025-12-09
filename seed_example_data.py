#!/usr/bin/env python
"""
Seed example data for all features:
- Suppliers (Proveedores)
- Transactions (Transacciones)
- Purchase Orders (Predictive)
- Rental Extensions (Extensiones)
"""
import os
import sys
from datetime import datetime, timedelta
import random

def seed_example_data(db=None, app=None):
    """Add example data to database
    
    Args:
        db: SQLAlchemy instance (if already in app context)
        app: Flask app instance
    """
    try:
        # If not passed in, import them
        if db is None:
            from app import app as _app, db as _db
            app = _app
            db = _db
            use_context = True
        else:
            use_context = False
        
        from models import User, Item, Supplier, Transaction, PurchaseOrder
        from werkzeug.security import generate_password_hash
        
        # Only use context if we imported app ourselves
        if use_context:
            with app.app_context():
            # 1. Create example suppliers (Proveedores)
            print("\n[1/4] Creating suppliers...")
            suppliers_data = [
                {
                    'name': 'Papelera Central',
                    'email': 'ventas@paperacentral.com',
                    'phone': '+57 301 1234567',
                    'city': 'Bogotá',
                    'contact': 'Juan Pérez'
                },
                {
                    'name': 'Distribuidora El Lápiz',
                    'email': 'contacto@lapiz.com',
                    'phone': '+57 312 9876543',
                    'city': 'Medellín',
                    'contact': 'María García'
                },
                {
                    'name': 'Importadora Escolar',
                    'email': 'import@escolar.co',
                    'phone': '+57 321 5555555',
                    'city': 'Cali',
                    'contact': 'Carlos López'
                },
                {
                    'name': 'Artículos de Oficina Premium',
                    'email': 'premium@oficina.co',
                    'phone': '+57 310 7777777',
                    'city': 'Barranquilla',
                    'contact': 'Ana Rodríguez'
                }
            ]
            
            for sup_data in suppliers_data:
                existing = Supplier.query.filter_by(name=sup_data['name']).first()
                if not existing:
                    supplier = Supplier(**sup_data)
                    db.session.add(supplier)
                    print(f"  OK {sup_data['name']}")
            db.session.commit()
            suppliers = Supplier.query.all()
            print(f"OK {len(suppliers)} suppliers created/verified")
            
            # 2. Create example student users
            print("\n[2/4] Creating example students...")
            students_data = [
                {'username': 'juan.perez', 'email': 'juan@university.edu', 'name': 'Juan Pérez'},
                {'username': 'maria.garcia', 'email': 'maria@university.edu', 'name': 'María García'},
                {'username': 'carlos.lopez', 'email': 'carlos@university.edu', 'name': 'Carlos López'},
                {'username': 'ana.rodriguez', 'email': 'ana@university.edu', 'name': 'Ana Rodríguez'},
            ]
            
            for std_data in students_data:
                existing = User.query.filter_by(username=std_data['username']).first()
                if not existing:
                    student = User(
                        username=std_data['username'],
                        email=std_data['email'],
                        password_hash=generate_password_hash('student123'),
                        role='student'
                    )
                    db.session.add(student)
                    print(f"  OK {std_data['username']}")
            db.session.commit()
            students = User.query.filter_by(role='student').all()
            print(f"OK {len(students)} students created/verified")
            
            # 3. Create transactions (Compras y Rentas)
            print("\n[3/4] Creating example transactions...")
            items = Item.query.all()
            admin_user = User.query.filter_by(username='admin').first()
            
            transactions_created = 0
            # Create 20 random transactions
            for i in range(20):
                random_item = random.choice(items)
                random_student = random.choice(students)
                
                # 50% rentals, 50% sales
                is_rental = random.choice([True, False])
                trans_kind = 'rent' if is_rental else 'buy'
                
                # Random date in last 60 days
                days_ago = random.randint(0, 60)
                trans_date = datetime.utcnow() - timedelta(days=days_ago)
                
                transaction = Transaction(
                    user_id=random_student.id,
                    item_id=random_item.id,
                    kind=trans_kind,
                    qty=random.randint(1, 3),
                    timestamp=trans_date
                )
                
                # If rental, set dates
                if is_rental:
                    transaction.rent_start_date = trans_date.date()
                    transaction.rent_days = random.randint(3, 14)
                    transaction.rent_due_date = (trans_date + timedelta(days=transaction.rent_days)).date()
                    transaction.returned = random.choice([True, False])
                    if transaction.returned:
                        transaction.return_date = trans_date + timedelta(days=random.randint(2, 15))
                
                db.session.add(transaction)
                transactions_created += 1
                
                if transactions_created % 5 == 0:
                    print(f"  OK {transactions_created} transactions...")
            
            db.session.commit()
            print(f"OK {transactions_created} transactions created")
            
            # 4. Create purchase orders (for Predictive)
            print("\n[4/4] Creating example purchase orders...")
            
            po_created = 0
            # Create 15 purchase orders
            for i in range(15):
                random_supplier = random.choice(suppliers)
                random_item = random.choice(items)
                
                # Random date in last 90 days
                days_ago = random.randint(0, 90)
                po_date = datetime.utcnow() - timedelta(days=days_ago)
                
                purchase_order = PurchaseOrder(
                    supplier_id=random_supplier.id,
                    item_id=random_item.id,
                    quantity=random.randint(10, 100),
                    unit_price=random_item.price * 0.7,  # 30% discount
                    order_date=po_date,
                    expected_delivery_date=po_date + timedelta(days=random.randint(5, 30)),
                    status=random.choice(['pending', 'delivered', 'cancelled'])
                )
                purchase_order.total_cost = purchase_order.quantity * purchase_order.unit_price
                
                db.session.add(purchase_order)
                po_created += 1
                
                if po_created % 5 == 0:
                    print(f"  OK {po_created} purchase orders...")
            
            db.session.commit()
            print(f"OK {po_created} purchase orders created")
            
            # 5. Create rental extensions
            print("\n[5/5] Creating rental extension examples...")
            
            # Get pending rentals to add extensions
            rentals = Transaction.query.filter_by(kind='rent').limit(8).all()
            extensions_created = 0
            
            for rental in rentals:
                rental.extension_requested = True
                rental.extension_days = random.randint(3, 7)
                rental.extension_approved = True
                rental.extension_approved_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                extensions_created += 1
                print(f"  OK Extension for rental #{rental.id}")
            
            db.session.commit()
            print(f"OK {extensions_created} rental extensions created")
            
            # Summary
            print("\n" + "=" * 70)
            print("OK EXAMPLE DATA SEEDED SUCCESSFULLY")
            print("=" * 70)
            print(f"  Suppliers:           {len(suppliers)}")
            print(f"  Students:            {len(students)}")
            print(f"  Transactions:        {Transaction.query.count()}")
            print(f"  Purchase Orders:     {PurchaseOrder.query.count()}")
            print(f"  Rental Extensions:   {Transaction.query.filter_by(extension_requested=True).count()}")
            print("=" * 70 + "\n")
            
            return True
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = seed_example_data()
    sys.exit(0 if success else 1)
