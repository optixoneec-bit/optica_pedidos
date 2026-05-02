"""
Pedidos App - Admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Pedido, Campo, PedidoValor,
    EstadoPedido, Rol
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin para usuarios."""
    list_display = ['username', 'email', 'rol', 'nombre_optica', 'is_active', 'is_staff']
    list_filter = ['rol', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'nombre_optica', 'ruc_optica']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Datos de Óptica', {
            'fields': (
                'rol',
                'nombre_optica',
                'ciudad_optica',
                'ruc_optica',
                'vendedor_optica',
                'telefono_optica',
                'logo'
            )
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos de Óptica', {
            'fields': (
                'rol',
                'nombre_optica',
                'ciudad_optica',
                'ruc_optica',
                'vendedor_optica',
                'telefono_optica'
            )
        }),
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Admin para pedidos."""
    list_display = ['numero_orden', 'cliente', 'estado', 'nombre_optica', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['numero_orden', 'nombre_optica', 'cliente__username', 'cliente__ruc_optica']
    readonly_fields = ['numero_orden', 'uid', 'fecha_creacion', 'fecha_actualizacion', 'barcode']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = [
        ('Información General', {
            'fields': ['numero_orden', 'cliente', 'estado', 'fecha_creacion', 'barcode']
        }),
        ('Datos de la Óptica', {
            'fields': ['nombre_optica', 'ciudad_optica', 'ruc_optica', 'vendedor_optica', 'telefono_optica'],
            'classes': ['collapse']
        }),
        ('Tipo de Lente', {
            'fields': ['tipo_lente', 'diseno_lente'],
            'classes': ['collapse']
        }),
        ('Receta - O.D.', {
            'fields': ['od_esfera', 'od_cilindro', 'od_eje', 'od_dnp', 'od_altura', 'od_adicion'],
            'classes': ['collapse']
        }),
        ('Receta - O.I.', {
            'fields': ['oi_esfera', 'oi_cilindro', 'oi_eje', 'oi_dnp', 'oi_altura', 'oi_adicion'],
            'classes': ['collapse']
        }),
        ('Medidas Adicionales', {
            'fields': ['horizontal', 'vertical', 'puente', 'distancia_mecanica'],
            'classes': ['collapse']
        }),
        ('Montura', {
            'fields': ['montura_descripcion', 'montura_estado', 'montura_foto'],
            'classes': ['collapse']
        }),
        ('Bisel', {
            'fields': ['tipo_bisel'],
            'classes': ['collapse']
        }),
        ('Observaciones', {
            'fields': ['observaciones'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    """Admin para campos dinámicos."""
    list_display = ['nombre', 'clave', 'tipo', 'categoria', 'orden', 'activo']
    list_filter = ['tipo', 'categoria', 'activo']
    search_fields = ['nombre', 'clave']
    list_editable = ['orden', 'activo']


@admin.register(PedidoValor)
class PedidoValorAdmin(admin.ModelAdmin):
    """Admin para valores de campos."""
    list_display = ['pedido', 'campo', 'valor']
    list_filter = ['campo__categoria']
    search_fields = ['pedido__numero_orden', 'campo__nombre']