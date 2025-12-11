"""
Seed data for products - Initial inventory for stationery store
"""

PRODUCTS = {
    'Útiles de Escritura': [
        {'name': 'Bolígrafo azul', 'description': 'Bolígrafo de tinta azul - caja x12', 'price': 15000, 'stock': 150, 'rentable': False},
        {'name': 'Bolígrafo negro', 'description': 'Bolígrafo de tinta negra - caja x12', 'price': 15000, 'stock': 120, 'rentable': False},
        {'name': 'Lápiz HB', 'description': 'Lápiz de grafito HB - docena', 'price': 8000, 'stock': 200, 'rentable': False},
        {'name': 'Lápiz HB 2', 'description': 'Lápiz de grafito HB - docena (calidad premium)', 'price': 12000, 'stock': 100, 'rentable': False},
        {'name': 'Marcador permanente', 'description': 'Marcador permanente multicolor - caja x8', 'price': 18000, 'stock': 80, 'rentable': False},
        {'name': 'Corrector líquido', 'description': 'Corrector líquido blanco - frasco 20ml', 'price': 5000, 'stock': 60, 'rentable': False},
    ],
    'Cuadernos y Blocs': [
        {'name': 'Cuaderno 100 hojas', 'description': 'Cuaderno con 100 hojas rayadas - tamaño estándar', 'price': 12000, 'stock': 180, 'rentable': False},
        {'name': 'Cuaderno 200 hojas', 'description': 'Cuaderno con 200 hojas rayadas - tamaño estándar', 'price': 18000, 'stock': 140, 'rentable': False},
        {'name': 'Bloc de notas', 'description': 'Bloc de notas adhesivas - 100 hojas', 'price': 3500, 'stock': 250, 'rentable': False},
        {'name': 'Libreta de espiral', 'description': 'Libreta de espiral - 80 hojas tamaño A5', 'price': 9000, 'stock': 120, 'rentable': False},
    ],
    'Carpetas y Organizadores': [
        {'name': 'Carpeta de cartón', 'description': 'Carpeta de cartón con 2 solapas', 'price': 4500, 'stock': 300, 'rentable': False},
        {'name': 'Carpeta de plástico', 'description': 'Carpeta de plástico resistente - tamaño oficio', 'price': 6500, 'stock': 250, 'rentable': False},
        {'name': 'Archivador', 'description': 'Archivador con palanca - lomo 75mm', 'price': 25000, 'stock': 60, 'rentable': True},
        {'name': 'Organizador de escritorio', 'description': 'Organizador de escritorio - 6 compartimentos', 'price': 35000, 'stock': 40, 'rentable': True},
        {'name': 'Estantería metálica', 'description': 'Estantería metálica pequeña - 3 niveles', 'price': 120000, 'stock': 15, 'rentable': True},
    ],
    'Materiales de Oficina': [
        {'name': 'Pegamento en barra', 'description': 'Pegamento en barra - 40g', 'price': 3500, 'stock': 180, 'rentable': False},
        {'name': 'Pegamento líquido', 'description': 'Pegamento líquido blanco - botella 120ml', 'price': 6500, 'stock': 100, 'rentable': False},
        {'name': 'Cinta adhesiva', 'description': 'Cinta adhesiva transparente - rollo 48mm x 50m', 'price': 4000, 'stock': 200, 'rentable': False},
        {'name': 'Tijeras', 'description': 'Tijeras de acero inoxidable - tamaño mediano', 'price': 18000, 'stock': 90, 'rentable': False},
        {'name': 'Perforador', 'description': 'Perforador de metal - 2 agujeros', 'price': 22000, 'stock': 50, 'rentable': True},
        {'name': 'Grapadora', 'description': 'Grapadora de metal - capacidad 20 hojas', 'price': 28000, 'stock': 45, 'rentable': True},
        {'name': 'Cosedora', 'description': 'Cosedora manual - pequeña', 'price': 45000, 'stock': 20, 'rentable': True},
    ],
    'Papel y Cartulina': [
        {'name': 'Papel A4 blanco', 'description': 'Papel A4 blanco 75g - resma 500 hojas', 'price': 35000, 'stock': 80, 'rentable': False},
        {'name': 'Papel A4 de color', 'description': 'Papel A4 multicolor - paquete 250 hojas', 'price': 28000, 'stock': 100, 'rentable': False},
        {'name': 'Cartulina de colores', 'description': 'Cartulina de colores - paquete 50 hojas', 'price': 15000, 'stock': 120, 'rentable': False},
        {'name': 'Papel crepe', 'description': 'Papel crepe multicolor - 10 rollos', 'price': 12000, 'stock': 60, 'rentable': False},
    ],
    'Equipos y Herramientas': [
        {'name': 'Calculadora científica', 'description': 'Calculadora científica con 252 funciones', 'price': 85000, 'stock': 30, 'rentable': True},
        {'name': 'Regla 30cm', 'description': 'Regla de plástico - 30cm', 'price': 3500, 'stock': 150, 'rentable': False},
        {'name': 'Escuadra y cartabón', 'description': 'Set de escuadra y cartabón de plástico', 'price': 8500, 'stock': 100, 'rentable': False},
        {'name': 'Transportador', 'description': 'Transportador de plástico - 180°', 'price': 4500, 'stock': 80, 'rentable': False},
        {'name': 'Compás', 'description': 'Compás metálico con punta seca', 'price': 16000, 'stock': 70, 'rentable': False},
        {'name': 'Lámpara de escritorio', 'description': 'Lámpara LED de escritorio - ajustable', 'price': 95000, 'stock': 25, 'rentable': True},
        {'name': 'Lámpara de pie', 'description': 'Lámpara de pie LED - 3 intensidades', 'price': 180000, 'stock': 12, 'rentable': True},
    ],
    'Encuadernación': [
        {'name': 'Encuadernador espiral', 'description': 'Máquina encuadernadora de espiral plástico', 'price': 450000, 'stock': 5, 'rentable': True},
        {'name': 'Espirales plásticas', 'description': 'Espirales plásticas - caja 100 piezas', 'price': 35000, 'stock': 40, 'rentable': False},
        {'name': 'Anillas metálicas', 'description': 'Anillas metálicas - caja 250 piezas', 'price': 22000, 'stock': 60, 'rentable': False},
        {'name': 'Encuadernador térmico', 'description': 'Máquina encuadernadora térmica - hasta 300 hojas', 'price': 550000, 'stock': 3, 'rentable': True},
    ],
    'Mochilas y Maletines': [
        {'name': 'Mochila escolar', 'description': 'Mochila escolar - capacidad 30L', 'price': 75000, 'stock': 45, 'rentable': True},
        {'name': 'Maletín ejecutivo', 'description': 'Maletín profesional - cierre de seguridad', 'price': 180000, 'stock': 20, 'rentable': True},
        {'name': 'Bolsa de documentos', 'description': 'Bolsa resistente para documentos - tamaño A4', 'price': 35000, 'stock': 80, 'rentable': False},
    ],
    'Artículos de Decoración': [
        {'name': 'Stickers decorativos', 'description': 'Set de stickers - 100 piezas variadas', 'price': 12000, 'stock': 150, 'rentable': False},
        {'name': 'Rotuladores de colores', 'description': 'Set de rotuladores - 24 colores', 'price': 28000, 'stock': 70, 'rentable': False},
        {'name': 'Afiches y carteles', 'description': 'Afiches educativos variados - paquete 5', 'price': 18000, 'stock': 100, 'rentable': False},
        {'name': 'Pizarra blanca', 'description': 'Pizarra blanca magnética - 40x60cm', 'price': 65000, 'stock': 25, 'rentable': True},
        {'name': 'Tablero de corcho', 'description': 'Tablero de corcho - 60x90cm', 'price': 58000, 'stock': 30, 'rentable': True},
    ],
}
