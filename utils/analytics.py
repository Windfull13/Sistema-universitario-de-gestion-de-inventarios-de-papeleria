"""Análisis e IA: demanda estacional, recomendaciones, analytics"""
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func
from models import Transaction, Item, db
import logging
import statistics

logger = logging.getLogger(__name__)

def forecast_revenue(weeks=12):
    """Predice ingresos para las próximas 12 semanas basado en datos históricos"""
    try:
        # Obtener transacciones de compra de últimas 12 semanas
        twelve_weeks_ago = datetime.utcnow() - timedelta(weeks=12)
        
        sales_by_week = defaultdict(float)
        
        transactions = Transaction.query.filter(
            Transaction.kind.in_(['buy', 'rent']),
            Transaction.timestamp >= twelve_weeks_ago
        ).all()
        
        for tx in transactions:
            if tx.timestamp and tx.item:
                week_num = tx.timestamp.isocalendar()[1]
                revenue = tx.item.price * tx.qty
                sales_by_week[week_num] += revenue
        
        if not sales_by_week:
            return {
                'forecast': {},
                'average_weekly': 0,
                'trend': 'Sin datos',
                'confidence': 0
            }
        
        # Calcular promedio y tendencia
        weekly_values = list(sales_by_week.values())
        avg_weekly = statistics.mean(weekly_values) if weekly_values else 0
        
        # Análisis de tendencia
        if len(weekly_values) > 2:
            recent_avg = statistics.mean(weekly_values[-4:]) if len(weekly_values) >= 4 else weekly_values[-1]
            old_avg = statistics.mean(weekly_values[:4]) if len(weekly_values) >= 4 else weekly_values[0]
            trend_percent = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
            
            if trend_percent > 10:
                trend = "📈 Crecimiento Fuerte"
            elif trend_percent > 0:
                trend = "📊 Crecimiento Moderado"
            elif trend_percent > -10:
                trend = "📉 Ligera Caída"
            else:
                trend = "📉 Caída Significativa"
        else:
            trend = "Sin suficientes datos"
            trend_percent = 0
        
        # Generar forecast para próximas 12 semanas
        forecast = {}
        today = datetime.utcnow()
        
        for i in range(1, 13):
            future_date = today + timedelta(weeks=i)
            week_num = future_date.isocalendar()[1]
            
            # Predicción conservadora: promedio histórico con ajuste de tendencia
            base_forecast = avg_weekly
            trend_adjustment = (trend_percent / 100) * avg_weekly
            predicted_revenue = base_forecast + (trend_adjustment * (i / 12))
            
            forecast[f"Sem {i}"] = {
                'date': future_date.strftime('%d/%m/%Y'),
                'predicted_revenue': round(predicted_revenue, 0),
                'confidence': max(50, min(95, 70 + (len(weekly_values) * 2)))
            }
        
        return {
            'forecast': forecast,
            'average_weekly': round(avg_weekly, 0),
            'total_historical': round(sum(weekly_values), 0),
            'trend': trend,
            'trend_percent': round(trend_percent, 1),
            'confidence': max(50, min(95, 70 + (len(weekly_values) * 2)))
        }
    
    except Exception as e:
        logger.error(f"Error en forecast_revenue: {str(e)}")
        return {
            'forecast': {},
            'average_weekly': 0,
            'trend': 'Error en cálculo',
            'confidence': 0,
            'error': str(e)
        }

def get_trending_products(days=30, limit=8):
    """Identifica productos en tendencia (crecimiento en demanda)"""
    try:
        today = datetime.utcnow().date()
        period_days = days
        
        first_half_start = today - timedelta(days=period_days)
        first_half_end = today - timedelta(days=period_days // 2)
        second_half_start = today - timedelta(days=period_days // 2)
        second_half_end = today
        
        # Transacciones primera mitad
        first_period = db.session.query(
            Item.id,
            Item.name,
            Item.category,
            Item.price,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.qty).label('total_qty')
        ).join(Transaction).filter(
            Transaction.timestamp >= first_half_start,
            Transaction.timestamp <= first_half_end,
            Transaction.kind.in_(['buy', 'rent'])
        ).group_by(Item.id).all()
        
        # Transacciones segunda mitad
        second_period = db.session.query(
            Item.id,
            Item.name,
            Item.category,
            Item.price,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.qty).label('total_qty')
        ).join(Transaction).filter(
            Transaction.timestamp >= second_half_start,
            Transaction.timestamp <= second_half_end,
            Transaction.kind.in_(['buy', 'rent'])
        ).group_by(Item.id).all()
        
        # Crear dict para comparación
        first_dict = {item[0]: {'count': item[4], 'qty': item[5] or 0, 'name': item[1], 'category': item[2], 'price': item[3]} for item in first_period}
        second_dict = {item[0]: {'count': item[4], 'qty': item[5] or 0, 'name': item[1], 'category': item[2], 'price': item[3]} for item in second_period}
        
        # Calcular growth
        trending = []
        
        for item_id, second_data in second_dict.items():
            first_data = first_dict.get(item_id, {'count': 0, 'qty': 0})
            first_count = first_data.get('count', 0)
            
            if first_count > 0:
                growth = ((second_data['count'] - first_count) / first_count) * 100
            else:
                growth = 100 if second_data['count'] > 0 else 0
            
            if growth > 0:  # Solo items en crecimiento
                trending.append({
                    'item_id': item_id,
                    'name': second_data['name'],
                    'category': second_data['category'],
                    'price': second_data['price'],
                    'growth_percent': round(growth, 1),
                    'current_transactions': second_data['count'],
                    'previous_transactions': first_count,
                    'momentum': 'Explosión' if growth > 100 else ('Fuerte' if growth > 50 else ('Moderado' if growth > 25 else 'Leve'))
                })
        
        # Ordenar por growth y retornar top
        trending_sorted = sorted(trending, key=lambda x: x['growth_percent'], reverse=True)
        return trending_sorted[:limit]
    
    except Exception as e:
        logger.error(f"Error en get_trending_products: {str(e)}")
        return []

def get_predictive_analytics():
    """Combina revenue forecast y trending products para panel predictivo"""
    try:
        revenue_forecast = forecast_revenue(weeks=12)
        trending_products = get_trending_products(days=30, limit=8)
        
        # Calcular métricas de confianza global
        total_transactions = Transaction.query.count()
        confidence_score = min(95, 60 + (min(total_transactions, 1000) / 1000 * 35))
        
        return {
            'revenue_forecast': revenue_forecast,
            'trending_products': trending_products,
            'confidence_score': round(confidence_score, 1),
            'last_updated': datetime.utcnow().strftime('%d/%m/%Y %H:%M'),
            'data_points': total_transactions
        }
    
    except Exception as e:
        logger.error(f"Error en get_predictive_analytics: {str(e)}")
        return {
            'revenue_forecast': {},
            'trending_products': [],
            'confidence_score': 0,
            'error': str(e)
        }


def calculate_seasonal_demand():
    """Analiza patrones estacionales y predice demanda para próximos 3 meses"""
    try:
        all_transactions = Transaction.query.filter(
            Transaction.timestamp != None
        ).all()
        
        if not all_transactions:
            return {'peaks': {}, 'forecast': {}, 'seasonal_pattern': {}}
        
        seasonal_pattern = defaultdict(int)
        
        for t in all_transactions:
            if t.timestamp:
                month = t.timestamp.month
                month_name = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][month - 1]
                seasonal_pattern[month_name] += 1
        
        if seasonal_pattern:
            avg_transactions = sum(seasonal_pattern.values()) / len(seasonal_pattern)
            peaks = {}
            
            back_to_school = ['Julio', 'Agosto', 'Septiembre']
            christmas = ['Noviembre', 'Diciembre']
            midterm = ['Marzo', 'Octubre', 'Noviembre']
            
            for month, count in seasonal_pattern.items():
                if month in back_to_school:
                    peaks[month] = {
                        'type': 'Escolar (Vuelta a clases)',
                        'intensity': count / avg_transactions if avg_transactions > 0 else 1
                    }
                elif month in christmas:
                    peaks[month] = {
                        'type': 'Fin de Año',
                        'intensity': count / avg_transactions if avg_transactions > 0 else 1
                    }
                elif month in midterm and count > avg_transactions:
                    peaks[month] = {
                        'type': 'Semana de Parciales',
                        'intensity': count / avg_transactions if avg_transactions > 0 else 1
                    }
            
            today = datetime.utcnow()
            current_month = today.month
            forecast = {}
            
            for i in range(1, 4):
                future_month = (current_month + i - 1) % 12 + 1
                month_name = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][future_month - 1]
                
                historical = seasonal_pattern.get(month_name, 0)
                predicted = int(historical * 1.05) if historical > 0 else int(avg_transactions)
                peak_indicator = 'Alza' if predicted > avg_transactions * 1.2 else 'Normal'
                
                forecast[month_name] = {
                    'predicted_transactions': predicted,
                    'trend': peak_indicator,
                    'vs_average': f"+{((predicted / avg_transactions - 1) * 100):.0f}%" if avg_transactions > 0 else "0%"
                }
            
            return {
                'peaks': peaks,
                'forecast': forecast,
                'seasonal_pattern': dict(seasonal_pattern),
                'average_monthly': int(avg_transactions)
            }
    
    except Exception as e:
        logger.error(f"Error en calculate_seasonal_demand: {str(e)}")
        return {'peaks': {}, 'forecast': {}, 'seasonal_pattern': {}, 'error': str(e)}

def get_analytics_data():
    """Obtiene datos completos para analytics/dashboard"""
    from models import db
    
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Estadísticas generales
    total_items = Item.query.count()
    total_rentable = Item.query.filter_by(rentable=True).count()
    active_rentals = Transaction.query.filter_by(kind='rent', returned=False).count()
    overdue_count = Transaction.query.filter(
        Transaction.kind == 'rent',
        Transaction.returned == False,
        Transaction.rent_due_date < today
    ).count()
    
    # Por categoría
    categories = db.session.query(
        Item.category,
        func.count(Item.id).label('count'),
        func.sum(Item.stock).label('total_stock')
    ).group_by(Item.category).all()
    
    # Transacciones últimos 30 días
    daily_transactions = db.session.query(
        func.date(Transaction.timestamp).label('date'),
        func.count(Transaction.id).label('count'),
        Transaction.kind
    ).filter(Transaction.timestamp >= thirty_days_ago).group_by(
        func.date(Transaction.timestamp),
        Transaction.kind
    ).all()
    
    # Productos populares
    popular = db.session.query(
        Item.name,
        func.count(Transaction.id).label('count')
    ).join(Transaction).group_by(Item.id).order_by(
        func.count(Transaction.id).desc()
    ).limit(5).all()
    
    popular_items = [{'name': r[0], 'transaction_count': int(r[1] or 0)} for r in popular]
    
    # Duración promedio renta
    avg_duration = db.session.query(
        func.avg(Transaction.rent_days)
    ).filter(Transaction.kind == 'rent').scalar() or 0
    
    # Stock bajo
    low_stock = Item.query.filter(
        Item.stock <= (2 if Item.rentable else 10)
    ).all()
    
    # Recomendaciones de reposición
    reorder = []
    for item in Item.query.all():
        if item.stock and item.stock <= (2 if item.rentable else 10):
            total_tx = db.session.query(func.count(Transaction.id)).filter(
                Transaction.item_id == item.id
            ).scalar() or 0
            
            recent_tx = db.session.query(func.count(Transaction.id)).filter(
                Transaction.item_id == item.id,
                Transaction.timestamp >= thirty_days_ago
            ).scalar() or 0
            
            consumption = recent_tx / 30.0 if recent_tx > 0 else 0
            min_stock = max(2 if item.rentable else 10, int(consumption * 7))
            
            score = (recent_tx * 40) + ((min_stock - item.stock) * 30) + (total_tx * 0.3)
            
            reorder.append({
                'item': item,
                'score': score,
                'consumption_rate': round(consumption, 2),
                'recommended_stock': min_stock
            })
    
    top_reorder = sorted(reorder, key=lambda x: x['score'], reverse=True)[:3]
    
    return {
        'general': {
            'total_items': total_items,
            'total_rentable': total_rentable,
            'active_rentals': active_rentals,
            'overdue_count': overdue_count,
            'avg_rental_duration': round(avg_duration, 1)
        },
        'categories': categories,
        'daily_transactions': daily_transactions,
        'popular_items': popular_items,
        'low_stock_items': low_stock,
        'reorder_recommendation': top_reorder,
        'seasonal_demand': calculate_seasonal_demand()
    }

def analyze_slow_suppliers():
    """Identifica proveedores lentos (entregas atrasadas)"""
    try:
        from models import Supplier, PurchaseOrder
        
        suppliers_analysis = []
        
        suppliers = Supplier.query.all()
        
        for supplier in suppliers:
            # Órdenes completadas
            completed_orders = PurchaseOrder.query.filter(
                PurchaseOrder.supplier_id == supplier.id,
                PurchaseOrder.status == 'delivered'
            ).all()
            
            # Órdenes retrasadas
            delayed_orders = PurchaseOrder.query.filter(
                PurchaseOrder.supplier_id == supplier.id,
                PurchaseOrder.status == 'delayed'
            ).count()
            
            # Órdenes pendientes
            pending_orders = PurchaseOrder.query.filter(
                PurchaseOrder.supplier_id == supplier.id,
                PurchaseOrder.status == 'pending'
            ).count()
            
            if not completed_orders and pending_orders == 0:
                continue  # Sin historial
            
            # Calcular promedio de días de entrega
            total_days = 0
            for order in completed_orders:
                if order.expected_delivery_date and order.actual_delivery_date:
                    days = (order.actual_delivery_date - order.expected_delivery_date).days
                    total_days += max(0, days)  # Solo contar retrasos
            
            avg_delay_days = total_days / len(completed_orders) if completed_orders else 0
            
            # Calcular tasa de puntualidad
            on_time = sum(1 for o in completed_orders if not o.is_overdue())
            punctuality_rate = (on_time / len(completed_orders) * 100) if completed_orders else 100
            
            # Clasificar riesgo
            if avg_delay_days > 5 or punctuality_rate < 60:
                risk_level = "🔴 ALTO"
            elif avg_delay_days > 2 or punctuality_rate < 80:
                risk_level = "🟡 MEDIO"
            else:
                risk_level = "🟢 BAJO"
            
            suppliers_analysis.append({
                'supplier_id': supplier.id,
                'name': supplier.name,
                'contact': supplier.contact,
                'city': supplier.city,
                'total_orders': len(completed_orders) + delayed_orders + pending_orders,
                'completed_orders': len(completed_orders),
                'delayed_orders': delayed_orders,
                'pending_orders': pending_orders,
                'avg_delay_days': round(avg_delay_days, 1),
                'punctuality_rate': round(punctuality_rate, 1),
                'risk_level': risk_level,
                'items_supplied': len(supplier.items)
            })
        
        return sorted(suppliers_analysis, key=lambda x: x['avg_delay_days'], reverse=True)
    
    except Exception as e:
        logger.error(f"Error en analyze_slow_suppliers: {str(e)}")
        return []

def analyze_slow_rotation():
    """Identifica productos con rotación lenta"""
    try:
        today = datetime.utcnow().date()
        thirty_days_ago = today - timedelta(days=30)
        
        slow_rotation_items = []
        
        items = Item.query.all()
        
        for item in items:
            # Transacciones últimos 30 días
            recent_sales = Transaction.query.filter(
                Transaction.item_id == item.id,
                Transaction.kind.in_(['buy', 'rent']),
                Transaction.timestamp >= thirty_days_ago
            ).count()
            
            # Transacciones últimas 12 semanas
            twelve_weeks_ago = today - timedelta(weeks=12)
            historical_sales = Transaction.query.filter(
                Transaction.item_id == item.id,
                Transaction.kind.in_(['buy', 'rent']),
                Transaction.timestamp >= twelve_weeks_ago
            ).count()
            
            # Calcular velocidad
            daily_velocity = recent_sales / 30.0
            historical_velocity = historical_sales / 84.0 if historical_sales > 0 else 0
            
            # Determinar si es lento
            if daily_velocity < 0.5 and item.stock > 5:  # Menos de 1 cada 2 días
                rotation_status = "🐢 LENTO"
                priority = "ALTO"
            elif daily_velocity < 1.0 and item.stock > 10:
                rotation_status = "🚶 MODERADO"
                priority = "MEDIO"
            else:
                rotation_status = "⚡ RÁPIDO"
                priority = "BAJO"
            
            # Si tiene rotación histórica pero ahora es lenta
            if historical_velocity > 1 and daily_velocity < 0.3:
                trend = "📉 CAÍDA FUERTE"
            elif daily_velocity > historical_velocity:
                trend = "📈 MEJORANDO"
            else:
                trend = "➡️ ESTABLE"
            
            # Obtener nombre de proveedor de forma safe
            supplier_name = 'Sin proveedor'
            try:
                if hasattr(item, 'supplier') and item.supplier:
                    supplier_name = item.supplier.name
            except:
                supplier_name = 'Sin proveedor'
            
            if rotation_status != "⚡ RÁPIDO":  # Solo reportar items lento/moderados
                slow_rotation_items.append({
                    'item_id': item.id,
                    'name': item.name,
                    'category': item.category,
                    'supplier_id': getattr(item, 'supplier_id', None),
                    'supplier_name': supplier_name,
                    'price': item.price,
                    'stock': item.stock,
                    'recent_sales_30d': recent_sales,
                    'daily_velocity': round(daily_velocity, 2),
                    'historical_velocity': round(historical_velocity, 2),
                    'rotation_status': rotation_status,
                    'trend': trend,
                    'priority': priority
                })
        
        return sorted(slow_rotation_items, key=lambda x: x['daily_velocity'])
    
    except Exception as e:
        logger.error(f"Error en analyze_slow_rotation: {str(e)}")
        return []

def analyze_supplier_comparison():
    """Compara desempeño entre proveedores para mismo producto"""
    try:
        from models import Supplier, PurchaseOrder
        
        supplier_comparison = {}
        
        # Agrupar items por categoría de forma safe
        try:
            categories = db.session.query(Item.category).distinct().all()
        except:
            return {}
        
        for cat_tuple in categories:
            category = cat_tuple[0]
            if not category:
                continue
            
            # Items en esta categoría
            items_in_cat = Item.query.filter_by(category=category).all()
            
            suppliers_in_cat = {}
            for item in items_in_cat:
                supplier_id = getattr(item, 'supplier_id', None)
                if not supplier_id:
                    try:
                        from models import Supplier
                        supplier = Supplier.query.filter_by(id=supplier_id).first()
                        if not supplier:
                            continue
                    except:
                        continue
                else:
                    continue
                
                supplier = Supplier.query.filter_by(id=supplier_id).first() if supplier_id else None
                if not supplier:
                    continue
                
                if supplier_id not in suppliers_in_cat:
                    suppliers_in_cat[supplier_id] = {
                        'name': supplier.name,
                        'items': [],
                        'avg_price': 0,
                        'avg_punctuality': 0,
                        'total_items': 0
                    }
                
                suppliers_in_cat[supplier_id]['items'].append(item.name)
                suppliers_in_cat[supplier_id]['avg_price'] += item.price
                suppliers_in_cat[supplier_id]['total_items'] += 1
                
                # Obtener puntualidad
                try:
                    from models import PurchaseOrder
                    completed = PurchaseOrder.query.filter(
                        PurchaseOrder.supplier_id == supplier_id,
                        PurchaseOrder.status == 'delivered'
                    ).count()
                    
                    if completed > 0:
                        on_time = sum(1 for o in PurchaseOrder.query.filter(
                            PurchaseOrder.supplier_id == supplier_id,
                            PurchaseOrder.status == 'delivered'
                        ).all() if not o.is_overdue())
                        suppliers_in_cat[supplier_id]['avg_punctuality'] = (on_time / completed * 100)
                except:
                    suppliers_in_cat[supplier_id]['avg_punctuality'] = 100
            
            if suppliers_in_cat:
                # Calcular promedios
                for sup_id, data in suppliers_in_cat.items():
                    data['avg_price'] = round(data['avg_price'] / data['total_items'], 0) if data['total_items'] > 0 else 0
                    data['avg_punctuality'] = round(data['avg_punctuality'], 1)
                
                supplier_comparison[category] = suppliers_in_cat
        
        return supplier_comparison
    
    except Exception as e:
        logger.error(f"Error en analyze_supplier_comparison: {str(e)}")
        return {}

def get_supplier_intelligence():
    """Orquesta análisis completo de proveedores"""
    try:
        slow_suppliers = analyze_slow_suppliers()
        slow_rotation = analyze_slow_rotation()
        supplier_comparison = analyze_supplier_comparison()
        
        # Generar recomendaciones
        recommendations = []
        
        # Recomendaciones por proveedores lentos
        for supplier in slow_suppliers:
            if supplier['risk_level'] == "🔴 ALTO":
                recommendations.append({
                    'type': 'Cambiar proveedor',
                    'target': supplier['name'],
                    'reason': f"Retraso promedio: {supplier['avg_delay_days']} días",
                    'action': f"Buscar alternativa. Afecta {supplier['items_supplied']} productos.",
                    'severity': 'CRÍTICO'
                })
            elif supplier['risk_level'] == "🟡 MEDIO":
                recommendations.append({
                    'type': 'Negociar SLA',
                    'target': supplier['name'],
                    'reason': f"Puntualidad: {supplier['punctuality_rate']}%",
                    'action': 'Establecer acuerdos de nivel de servicio más estrictos',
                    'severity': 'ALTO'
                })
        
        # Recomendaciones por rotación lenta
        for item in slow_rotation[:5]:  # Top 5 productos lentos
            recommendations.append({
                'type': 'Revisar proveedores',
                'target': item['name'],
                'reason': f"Rotación lenta ({item['daily_velocity']} items/día)",
                'action': f"Comparar precio/disponibilidad con {item['supplier_name']}",
                'severity': 'MEDIO'
            })
        
        return {
            'slow_suppliers': slow_suppliers,
            'slow_rotation': slow_rotation,
            'supplier_comparison': supplier_comparison,
            'recommendations': recommendations,
            'last_updated': datetime.utcnow().strftime('%d/%m/%Y %H:%M')
        }
    
    except Exception as e:
        logger.error(f"Error en get_supplier_intelligence: {str(e)}")
        return {
            'slow_suppliers': [],
            'slow_rotation': [],
            'supplier_comparison': {},
            'recommendations': [],
            'error': str(e)
        }

