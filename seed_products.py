#!/usr/bin/env python
"""
Seed products into the database
Complete list of stationery products organized by category
"""

PRODUCTS = {
    "Papeles": [
        {"name": "Hojas tamaño carta", "description": "Resma de 500 hojas tamaño carta", "price": 15000, "stock": 50, "rentable": False},
        {"name": "Hojas tamaño oficio", "description": "Resma de 500 hojas tamaño oficio", "price": 18000, "stock": 40, "rentable": False},
        {"name": "Papel bond", "description": "Papel bond blanco 75g", "price": 12000, "stock": 60, "rentable": False},
        {"name": "Papel periódico", "description": "Papel periódico rollo", "price": 8000, "stock": 30, "rentable": False},
        {"name": "Papel reciclado", "description": "Papel reciclado resma", "price": 20000, "stock": 25, "rentable": False},
        {"name": "Papel iris de colores", "description": "Paquete de 25 hojas colores surtidos", "price": 10000, "stock": 45, "rentable": False},
        {"name": "Cartulina opalina", "description": "Cartulina opalina paquete", "price": 12000, "stock": 35, "rentable": False},
        {"name": "Cartulina iris", "description": "Cartulina iris colores surtidos", "price": 11000, "stock": 40, "rentable": False},
        {"name": "Cartón paja", "description": "Pliego de cartón paja", "price": 5000, "stock": 20, "rentable": False},
        {"name": "Papel mantequilla", "description": "Rollo de papel mantequilla", "price": 7000, "stock": 30, "rentable": False},
        {"name": "Papel carbón", "description": "Block de papel carbón", "price": 6000, "stock": 25, "rentable": False},
        {"name": "Papel transferencia", "description": "Papel transferencia paquete", "price": 8500, "stock": 20, "rentable": False},
        {"name": "Papel fotográfico", "description": "Papel fotográfico 10x15cm", "price": 25000, "stock": 15, "rentable": False},
        {"name": "Cartulina bristol", "description": "Cartulina bristol blanca", "price": 9000, "stock": 35, "rentable": False},
        {"name": "Cartulina fluorescente", "description": "Cartulina fluorescente colores", "price": 13000, "stock": 25, "rentable": False},
        {"name": "Papel kraft", "description": "Papel kraft rollo", "price": 14000, "stock": 30, "rentable": False},
        {"name": "Foamy goma eva", "description": "Goma EVA colores variados", "price": 9500, "stock": 40, "rentable": False},
        {"name": "Papel celofán", "description": "Papel celofán paquete colores", "price": 7000, "stock": 35, "rentable": False},
        {"name": "Papel crepé", "description": "Papel crepé colores surtidos", "price": 6000, "stock": 40, "rentable": False},
        {"name": "Papel aluminio", "description": "Rollo de papel aluminio", "price": 8000, "stock": 25, "rentable": False},
        {"name": "Papel adhesivo sticker", "description": "Papel adhesivo para stickers", "price": 7500, "stock": 30, "rentable": False},
        {"name": "Papel etiqueta", "description": "Rollo de papel etiqueta", "price": 6500, "stock": 28, "rentable": False},
    ],
    "Escritura": [
        {"name": "Lápiz de grafito HB", "description": "Lápiz de grafito HB docena", "price": 8000, "stock": 100, "rentable": False},
        {"name": "Lápiz de grafito 2B", "description": "Lápiz de grafito 2B docena", "price": 9000, "stock": 80, "rentable": False},
        {"name": "Lápiz de grafito 2H", "description": "Lápiz de grafito 2H docena", "price": 9000, "stock": 70, "rentable": False},
        {"name": "Lapicero esfero azul", "description": "Pack de 12 lapiceros azules", "price": 7000, "stock": 150, "rentable": False},
        {"name": "Lapicero esfero rojo", "description": "Pack de 12 lapiceros rojos", "price": 7000, "stock": 120, "rentable": False},
        {"name": "Lapicero esfero negro", "description": "Pack de 12 lapiceros negros", "price": 7000, "stock": 140, "rentable": False},
        {"name": "Marcador permanente", "description": "Pack de marcadores permanentes", "price": 15000, "stock": 40, "rentable": False},
        {"name": "Marcador borrable", "description": "Pack de marcadores borrables", "price": 12000, "stock": 50, "rentable": False},
        {"name": "Resaltador", "description": "Pack de resaltadores colores", "price": 11000, "stock": 60, "rentable": False},
        {"name": "Portaminas", "description": "Portaminas con minas incluidas", "price": 10000, "stock": 45, "rentable": False},
        {"name": "Minas para portaminas", "description": "Tubo de minas 0.5mm", "price": 3000, "stock": 100, "rentable": False},
        {"name": "Plumón escolar", "description": "Pack de plumones escolares", "price": 9000, "stock": 70, "rentable": False},
        {"name": "Pluma fuente", "description": "Pluma fuente básica", "price": 25000, "stock": 20, "rentable": True},
        {"name": "Corrector líquido", "description": "Botella de corrector líquido", "price": 4500, "stock": 60, "rentable": False},
        {"name": "Corrector en cinta", "description": "Cinta correctora", "price": 6000, "stock": 50, "rentable": False},
        {"name": "Tinta para plumas", "description": "Frasco de tinta para plumas", "price": 8000, "stock": 30, "rentable": False},
        {"name": "Crayolas", "description": "Caja de 24 crayolas", "price": 9000, "stock": 80, "rentable": False},
        {"name": "Colores de madera", "description": "Caja de 24 colores de madera", "price": 18000, "stock": 50, "rentable": False},
        {"name": "Colores metálicos", "description": "Caja de colores metálicos y neon", "price": 22000, "stock": 30, "rentable": False},
    ],
    "Cuadernos y libretas": [
        {"name": "Cuaderno cosido", "description": "Cuaderno cosido 100 hojas rayadas", "price": 12000, "stock": 80, "rentable": False},
        {"name": "Cuaderno argollado", "description": "Cuaderno argollado 80 hojas", "price": 15000, "stock": 60, "rentable": False},
        {"name": "Libreta pequeña", "description": "Libreta de bolsillo 60 hojas", "price": 8000, "stock": 90, "rentable": False},
        {"name": "Block de notas", "description": "Block adhesivo colorido", "price": 5000, "stock": 100, "rentable": False},
        {"name": "Agenda", "description": "Agenda escolar 2025", "price": 30000, "stock": 40, "rentable": True},
        {"name": "Cuaderno universitario", "description": "Cuaderno 200 hojas rayadas", "price": 18000, "stock": 70, "rentable": False},
        {"name": "Cuaderno cuadriculado", "description": "Cuaderno cuadriculado 100 hojas", "price": 11000, "stock": 75, "rentable": False},
        {"name": "Cuaderno blanco", "description": "Cuaderno de papel blanco", "price": 13000, "stock": 65, "rentable": False},
        {"name": "Block de dibujo", "description": "Block de papel de dibujo", "price": 20000, "stock": 35, "rentable": False},
        {"name": "Cuaderno empastado", "description": "Cuaderno empastado tapa dura", "price": 25000, "stock": 25, "rentable": True},
    ],
    "Organización y archivo": [
        {"name": "Carpeta de anillas", "description": "Carpeta de anillas metálicas", "price": 18000, "stock": 50, "rentable": False},
        {"name": "Carpeta AZ", "description": "Carpeta AZ 26 divisiones", "price": 35000, "stock": 20, "rentable": True},
        {"name": "Carpeta con elástico", "description": "Carpeta con elástico", "price": 12000, "stock": 60, "rentable": False},
        {"name": "Portafolio", "description": "Portafolio de documentos", "price": 25000, "stock": 30, "rentable": True},
        {"name": "Archivador", "description": "Archivador de madera", "price": 45000, "stock": 15, "rentable": True},
        {"name": "Funda plástica", "description": "Paquete de fundas plásticas", "price": 8000, "stock": 100, "rentable": False},
        {"name": "Separadores", "description": "Juego de separadores", "price": 6000, "stock": 80, "rentable": False},
        {"name": "Gancho legajador", "description": "Gancho legajador metálico", "price": 3500, "stock": 150, "rentable": False},
        {"name": "Clips metálicos", "description": "Caja de clips variados", "price": 4000, "stock": 120, "rentable": False},
        {"name": "Grapadora para carpeta", "description": "Grapadora para encuadernar", "price": 15000, "stock": 25, "rentable": False},
        {"name": "Pasta L", "description": "Paquete de pastas L", "price": 5000, "stock": 100, "rentable": False},
        {"name": "Carpeta colgante", "description": "Carpeta colgante con guía", "price": 8000, "stock": 60, "rentable": False},
        {"name": "Sobre manila", "description": "Paquete de sobres manila", "price": 6000, "stock": 80, "rentable": False},
        {"name": "Sobre de correspondencia", "description": "Sobres blancos", "price": 7000, "stock": 90, "rentable": False},
        {"name": "Caja archivadora", "description": "Caja de cartón para archivo", "price": 12000, "stock": 40, "rentable": False},
    ],
    "Corte, pegado y fijación": [
        {"name": "Tijeras", "description": "Tijeras de acero inoxidable", "price": 15000, "stock": 50, "rentable": False},
        {"name": "Tijeras punta roma", "description": "Tijeras escolares punta roma", "price": 10000, "stock": 80, "rentable": False},
        {"name": "Bisturí cutter", "description": "Cutter de precisión", "price": 8000, "stock": 45, "rentable": False},
        {"name": "Repuestos de cutter", "description": "Paquete de cuchillas", "price": 5000, "stock": 100, "rentable": False},
        {"name": "Cinta transparente", "description": "Rollo de cinta transparente", "price": 3500, "stock": 150, "rentable": False},
        {"name": "Cinta masking tape", "description": "Cinta masking surtida", "price": 6000, "stock": 80, "rentable": False},
        {"name": "Cinta doble faz", "description": "Rollo de cinta doble cara", "price": 5000, "stock": 70, "rentable": False},
        {"name": "Pegante en barra", "description": "Pegante en barra 40g", "price": 4000, "stock": 120, "rentable": False},
        {"name": "Pegamento líquido", "description": "Frasco pegamento escolar", "price": 5000, "stock": 100, "rentable": False},
        {"name": "Silicona líquida", "description": "Tubo de silicona líquida", "price": 4500, "stock": 90, "rentable": False},
        {"name": "Silicona caliente", "description": "Barra de silicona caliente", "price": 3000, "stock": 150, "rentable": False},
        {"name": "Pistola de silicona", "description": "Pistola para silicona caliente", "price": 25000, "stock": 15, "rentable": True},
        {"name": "Grapadora", "description": "Grapadora de escritorio", "price": 20000, "stock": 30, "rentable": False},
        {"name": "Ganchos para grapas", "description": "Caja de ganchos para grapadora", "price": 8000, "stock": 60, "rentable": False},
        {"name": "Perforadora", "description": "Perforadora de dos agujeros", "price": 18000, "stock": 25, "rentable": False},
        {"name": "Imán autoadhesivo", "description": "Imán con adhesivo", "price": 6000, "stock": 50, "rentable": False},
        {"name": "Blue tack", "description": "Adhesivo reutilizable", "price": 8000, "stock": 40, "rentable": False},
    ],
    "Arte y manualidades": [
        {"name": "Tempera", "description": "Set de temperas 12 colores", "price": 12000, "stock": 50, "rentable": False},
        {"name": "Pintura acrílica", "description": "Set de acrílicos artísticos", "price": 35000, "stock": 20, "rentable": True},
        {"name": "Pinceles", "description": "Set de pinceles variados", "price": 15000, "stock": 40, "rentable": True},
        {"name": "Paleta para mezclar", "description": "Paleta de plástico", "price": 8000, "stock": 30, "rentable": False},
        {"name": "Lienzo", "description": "Lienzo 20x20cm", "price": 18000, "stock": 25, "rentable": True},
        {"name": "Plastilina", "description": "Caja de plastilina colores", "price": 9000, "stock": 60, "rentable": False},
        {"name": "Arcilla escolar", "description": "Pack de arcilla", "price": 7000, "stock": 50, "rentable": False},
        {"name": "Escarcha glitter", "description": "Frasco de escarcha colores", "price": 5000, "stock": 80, "rentable": False},
        {"name": "Stickers decorativos", "description": "Pack de stickers surtidos", "price": 6000, "stock": 70, "rentable": False},
        {"name": "Ojos locos", "description": "Paquete de ojos móviles", "price": 8000, "stock": 60, "rentable": False},
        {"name": "Limpiapipas", "description": "Pack de limpiapipas colores", "price": 5000, "stock": 90, "rentable": False},
        {"name": "Palos de paleta", "price": 6000, "description": "Paquete de palos de madera", "stock": 100, "rentable": False},
        {"name": "Cuentas abalorios", "description": "Bolsa de cuentas variadas", "price": 10000, "stock": 40, "rentable": False},
        {"name": "Foamy moldeable", "description": "Foamy para modelar", "price": 7500, "stock": 50, "rentable": False},
        {"name": "Papel decorativo", "description": "Pack de papel decorativo", "price": 8000, "stock": 60, "rentable": False},
        {"name": "Sellos de goma", "description": "Set de sellos de goma", "price": 12000, "stock": 30, "rentable": True},
        {"name": "Almohadilla para sellos", "description": "Almohadilla de tinta", "price": 5000, "stock": 50, "rentable": False},
        {"name": "Sellos infantiles", "description": "Set de sellos infantiles", "price": 9000, "stock": 45, "rentable": False},
    ],
    "Instrumentos de geometría": [
        {"name": "Regla", "description": "Regla de 30cm", "price": 3000, "stock": 150, "rentable": False},
        {"name": "Escuadra", "description": "Escuadra de 45 grados", "price": 4000, "stock": 130, "rentable": False},
        {"name": "Transportador", "description": "Transportador 180 grados", "price": 3500, "stock": 140, "rentable": False},
        {"name": "Compás", "description": "Compás escolar", "price": 8000, "stock": 70, "rentable": False},
        {"name": "Juego de geometría", "description": "Juego completo en estuche", "price": 20000, "stock": 35, "rentable": True},
        {"name": "Tiza blanca", "description": "Caja de tizas blancas", "price": 4000, "stock": 100, "rentable": False},
        {"name": "Tiza de colores", "description": "Caja de tizas de colores", "price": 5000, "stock": 90, "rentable": False},
        {"name": "Borrador para tablero", "description": "Borrador grande", "price": 6000, "stock": 50, "rentable": False},
    ],
    "Tecnología ligera": [
        {"name": "Memoria USB 32GB", "description": "Memoria USB de 32GB", "price": 35000, "stock": 20, "rentable": True},
        {"name": "Tarjeta SD 64GB", "description": "Tarjeta SD de 64GB", "price": 45000, "stock": 15, "rentable": True},
        {"name": "Adaptador USB", "description": "Adaptador USB tipo C", "price": 15000, "stock": 40, "rentable": False},
        {"name": "Audífonos económicos", "description": "Audífonos básicos", "price": 25000, "stock": 25, "rentable": True},
        {"name": "Cable USB", "description": "Cable USB tipo C", "price": 12000, "stock": 50, "rentable": False},
        {"name": "Cargador genérico", "description": "Cargador USB universal", "price": 30000, "stock": 20, "rentable": True},
        {"name": "Mouse básico", "description": "Mouse óptico", "price": 28000, "stock": 18, "rentable": True},
        {"name": "Teclado económico", "description": "Teclado USB", "price": 45000, "stock": 12, "rentable": True},
        {"name": "Protector para laptop", "description": "Funda protectora", "price": 35000, "stock": 15, "rentable": True},
        {"name": "Stylus barato", "description": "Lápiz digital", "price": 40000, "stock": 10, "rentable": True},
    ],
    "Impresión": [
        {"name": "Tóner para impresora", "description": "Tóner HP compatible", "price": 55000, "stock": 15, "rentable": True},
        {"name": "Tinta para impresora", "description": "Botellas de tinta de colores", "price": 35000, "stock": 20, "rentable": False},
        {"name": "Papel térmico", "description": "Rollo de papel térmico", "price": 12000, "stock": 30, "rentable": False},
        {"name": "Rollo para calculadora", "description": "Rollo de papel", "price": 5000, "stock": 60, "rentable": False},
    ],
    "Oficina": [
        {"name": "Calculadora básica", "description": "Calculadora de escritorio", "price": 25000, "stock": 30, "rentable": True},
        {"name": "Calculadora científica", "description": "Calculadora científica", "price": 45000, "stock": 15, "rentable": True},
        {"name": "Reloj de escritorio", "description": "Reloj digital", "price": 30000, "stock": 20, "rentable": True},
        {"name": "Portapapeles", "description": "Portapapeles con clip", "price": 12000, "stock": 40, "rentable": False},
        {"name": "Bandeja de documentos", "description": "Bandeja organizadora", "price": 18000, "stock": 25, "rentable": False},
        {"name": "Engrapadora industrial", "description": "Engrapadora de gran capacidad", "price": 50000, "stock": 10, "rentable": True},
        {"name": "Cinta métrica", "description": "Cinta métrica de 5m", "price": 12000, "stock": 35, "rentable": False},
        {"name": "Sello fechador", "description": "Sello fechador automático", "price": 22000, "stock": 20, "rentable": True},
        {"name": "Almohadilla para sello", "description": "Almohadilla de tinta", "price": 5000, "stock": 50, "rentable": False},
        {"name": "Libro contable diario", "description": "Libro contable", "price": 15000, "stock": 20, "rentable": True},
    ],
    "Escolares": [
        {"name": "Mochila", "description": "Mochila escolar", "price": 65000, "stock": 25, "rentable": True},
        {"name": "Lonchera", "description": "Lonchera térmica", "price": 35000, "stock": 30, "rentable": True},
        {"name": "Cartuchera", "description": "Cartuchera escolar", "price": 20000, "stock": 50, "rentable": False},
        {"name": "Regleta", "description": "Regleta magnética", "price": 8000, "stock": 40, "rentable": False},
        {"name": "Tarjetas didácticas", "description": "Set de tarjetas", "price": 12000, "stock": 35, "rentable": True},
        {"name": "Forro para cuadernos", "description": "Paquete de forros", "price": 8000, "stock": 80, "rentable": False},
        {"name": "Etiquetas escolares", "description": "Etiquetas adhesivas", "price": 6000, "stock": 90, "rentable": False},
        {"name": "Block de tareas", "description": "Block de tareas escolares", "price": 10000, "stock": 60, "rentable": False},
    ],
    "Otros productos": [
        {"name": "Pilas AA", "description": "Pack de pilas AA", "price": 8000, "stock": 80, "rentable": False},
        {"name": "Pilas AAA", "description": "Pack de pilas AAA", "price": 8000, "stock": 80, "rentable": False},
        {"name": "Llaveros", "description": "Llavero de metal", "price": 5000, "stock": 100, "rentable": False},
        {"name": "Candelas para tortas", "description": "Pack de candelas", "price": 6000, "stock": 70, "rentable": False},
        {"name": "Globos", "description": "Paquete de globos variados", "price": 8000, "stock": 60, "rentable": False},
        {"name": "Cuerda", "description": "Rollo de cuerda", "price": 7000, "stock": 50, "rentable": False},
        {"name": "Botones de manualidades", "description": "Set de botones", "price": 6000, "stock": 60, "rentable": False},
        {"name": "Regla flexible", "description": "Regla flexible de 30cm", "price": 5000, "stock": 70, "rentable": False},
        {"name": "Carpeta tipo acordeón", "description": "Carpeta con divisiones", "price": 15000, "stock": 35, "rentable": False},
        {"name": "Tarjetas de cumpleaños", "description": "Pack de tarjetas", "price": 10000, "stock": 40, "rentable": False},
        {"name": "Tarjetas de invitación", "description": "Pack de invitaciones", "price": 12000, "stock": 35, "rentable": False},
        {"name": "Sobres decorativos", "description": "Pack de sobres", "price": 8000, "stock": 50, "rentable": False},
        {"name": "Empaques para regalo", "description": "Caja de empaques", "price": 15000, "stock": 30, "rentable": False},
        {"name": "Cintas decorativas", "description": "Pack de cintas", "price": 10000, "stock": 45, "rentable": False},
        {"name": "Bolsas de papel", "description": "Pack de bolsas para regalo", "price": 12000, "stock": 40, "rentable": False},
    ]
}

def seed_products():
    """Add all products to database"""
    with app.app_context():
        print("=" * 70)
        print("AGREGANDO PRODUCTOS A LA BASE DE DATOS")
        print("=" * 70)
        
        try:
            # Check if products already exist
            existing = Item.query.first()
            if existing:
                count = Item.query.count()
                print("OK Base de datos ya tiene {} productos".format(count))
                return True
            
            total_added = 0
            for category, products in PRODUCTS.items():
                print("\n[CATEGORIA] {}".format(category))
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
                    print("  OK {}".format(product['name']))
                    total_added += 1
            
            db.session.commit()
            print("\n" + "=" * 70)
            print("OK {} PRODUCTOS AGREGADOS EXITOSAMENTE".format(total_added))
            print("=" * 70)
            return True
            
        except Exception as e:
            print("ERROR: {}".format(e))
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = seed_products()
    sys.exit(0 if success else 1)
