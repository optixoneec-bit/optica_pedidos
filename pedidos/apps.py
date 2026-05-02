"""
Pedidos App Configuration
"""
from django.apps import AppConfig


class PedidosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedidos'
    verbose_name = 'Pedidos'
    
    def ready(self):
        # Importar señales cuando la app esté lista
        pass