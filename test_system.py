#!/usr/bin/env python
"""
Script de prueba integral para verificar que todo el sistema funciona correctamente
"""

import sys
import os
from pathlib import Path

os.chdir(Path(__file__).parent)

from app import app, db
from models import User, Item, Supplier, PurchaseOrder, Transaction, ApiKey, LoginAttempt, ActiveSession
from utils.analytics import (
    get_analytics_data,
    get_trending_products,
    forecast_revenue,
    get_predictive_analytics,
    get_supplier_intelligence
)

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n" + "="*70)
    print("🗄️  TEST 1: CONEXIÓN A BASE DE DATOS")
    print("="*70)
    
    try:
        with app.app_context():
            users = User.query.count()
            items = Item.query.count()
            suppliers = Supplier.query.count()
            transactions = Transaction.query.count()
            
            print(f"✅ Conexión exitosa")
            print(f"   • Usuarios: {users}")
            print(f"   • Productos: {items}")
            print(f"   • Proveedores: {suppliers}")
            print(f"   • Transacciones: {transactions}")
            return True
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        return False

def test_analytics():
    """Probar funciones de analytics"""
    print("\n" + "="*70)
    print("📊 TEST 2: FUNCIONES DE ANALYTICS")
    print("="*70)
    
    try:
        with app.app_context():
            # Test general analytics
            analytics = get_analytics_data()
            print(f"✅ get_analytics_data()")
            print(f"   • Total items: {analytics.get('general', {}).get('total_items', 0)}")
            print(f"   • Active rentals: {analytics.get('general', {}).get('active_rentals', 0)}")
            
            # Test trending products
            trending = get_trending_products()
            print(f"✅ get_trending_products()")
            print(f"   • Trending items: {len(trending)}")
            
            # Test revenue forecast
            forecast = forecast_revenue()
            print(f"✅ forecast_revenue()")
            print(f"   • Forecast weeks: {len(forecast.get('weeks', []))}")
            
            return True
    except Exception as e:
        print(f"❌ Error en analytics: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predictive_analytics():
    """Probar analytics predictivo"""
    print("\n" + "="*70)
    print("🔮 TEST 3: ANALYTICS PREDICTIVO (IA)")
    print("="*70)
    
    try:
        with app.app_context():
            predictive = get_predictive_analytics()
            print(f"✅ get_predictive_analytics()")
            print(f"   • Revenue forecast confidence: {predictive.get('revenue_forecast', {}).get('confidence', 0)}%")
            print(f"   • Trending products: {len(predictive.get('trending_products', []))}")
            print(f"   • Last updated: {predictive.get('last_updated', 'N/A')}")
            
            return True
    except Exception as e:
        print(f"❌ Error en predictivo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supplier_intelligence():
    """Probar inteligencia de proveedores"""
    print("\n" + "="*70)
    print("🏢 TEST 4: INTELIGENCIA DE PROVEEDORES")
    print("="*70)
    
    try:
        with app.app_context():
            supplier_data = get_supplier_intelligence()
            print(f"✅ get_supplier_intelligence()")
            print(f"   • Slow suppliers: {len(supplier_data.get('slow_suppliers', []))}")
            print(f"   • Slow rotation items: {len(supplier_data.get('slow_rotation', []))}")
            print(f"   • Supplier comparisons: {len(supplier_data.get('supplier_comparison', {}))}")
            print(f"   • Recommendations: {len(supplier_data.get('recommendations', []))}")
            
            # Mostrar algunas recomendaciones
            recs = supplier_data.get('recommendations', [])[:3]
            if recs:
                print(f"\n   Top recomendaciones:")
                for i, rec in enumerate(recs, 1):
                    print(f"      {i}. {rec.get('title', 'N/A')} - {rec.get('severity', 'N/A')}")
            
            return True
    except Exception as e:
        print(f"❌ Error en proveedores: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Probar que las rutas están registradas"""
    print("\n" + "="*70)
    print("🛣️  TEST 5: RUTAS REGISTRADAS")
    print("="*70)
    
    try:
        routes_to_check = [
            '/admin/',
            '/admin/analytics',
            '/admin/predictive',
            '/admin/suppliers',
            '/admin/transactions',
            '/nfc-control',
            '/admin/rental-extensions'
        ]
        
        # Obtener todas las rutas
        routes = {}
        for rule in app.url_map.iter_rules():
            routes[rule.rule] = rule.endpoint
        
        all_found = True
        for route in routes_to_check:
            found = any(route in r for r in routes.keys())
            status = "✅" if found else "❌"
            print(f"{status} {route}")
            if not found:
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error al verificar rutas: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("🧪 PRUEBA INTEGRAL DEL SISTEMA")
    print("="*70)
    
    results = {
        "Base de Datos": test_database_connection(),
        "Analytics": test_analytics(),
        "Analytics Predictivo": test_predictive_analytics(),
        "Inteligencia de Proveedores": test_supplier_intelligence(),
        "Rutas": test_routes(),
    }
    
    print("\n" + "="*70)
    print("📋 RESUMEN DE RESULTADOS")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "-"*70)
    print(f"Pruebas pasadas: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo para usar.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
