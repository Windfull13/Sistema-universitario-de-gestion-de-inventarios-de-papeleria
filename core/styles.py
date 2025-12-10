"""
Utilidades compartidas para colores y estilos
"""

CATEGORY_COLORS = {
    'Papeles': '#E8F5E9',
    'Escritura': '#F3E5F5',
    'Cuadernos y libretas': '#E3F2FD',
    'Organización y archivo': '#FFF3E0',
    'Corte, pegado y fijación': '#FCE4EC',
    'Arte y manualidades': '#F1F8E9',
    'Instrumentos de geometría': '#E0F2F1',
    'Tecnología ligera': '#ECE7FF',
    'Impresión': '#F8F5FF',
    'Oficina': '#FFF8E1',
    'Escolares': '#E8EAF6',
    'Otros productos': '#F5F5F5'
}

TEXT_COLOR = (64, 64, 64)
DEFAULT_COLOR = '#F5F5F5'
DEFAULT_RGB = (245, 245, 245)


def hex_to_rgb(hex_color: str) -> tuple:
    """Convertir color hexadecimal a RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))


def get_category_color(category: str) -> tuple:
    """Obtener color RGB para una categoría"""
    hex_color = CATEGORY_COLORS.get(category, DEFAULT_COLOR)
    return hex_to_rgb(hex_color)
