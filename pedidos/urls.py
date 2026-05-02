"""
Pedidos App - URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Perfil
    path('perfil/', views.perfil, name='perfil'),
    
    # Pedidos
    path('pedidos/', views.pedido_list, name='pedido_list'),
    path('pedidos/nuevo/', views.pedido_create, name='pedido_create'),
    path('pedidos/<int:pk>/', views.pedido_detail, name='pedido_detail'),
    path('pedidos/<int:pk>/editar/', views.pedido_update, name='pedido_update'),
    path('pedidos/<int:pk>/estado/', views.pedido_cambiar_estado, name='pedido_cambiar_estado'),
    path('pedidos/<int:pk>/avanzar/', views.pedido_avanzar_estado, name='pedido_avanzar_estado'),
    path('pedidos/<int:pk>/pdf/', views.pedido_pdf, name='pedido_pdf'),
    path('pedidos/<int:pk>/eliminar/', views.pedido_eliminar, name='pedido_eliminar'),
    
    # Admin
    path('gestion/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('gestion/usuarios/nuevo/', views.admin_usuario_create, name='admin_usuario_create'),
    path('gestion/usuarios/<int:pk>/editar/', views.admin_usuario_edit, name='admin_usuario_edit'),
    
    path('gestion/campos/', views.admin_campos, name='admin_campos'),
    path('gestion/campos/nuevo/', views.admin_campo_create, name='admin_campo_create'),
    path('gestion/campos/<int:pk>/editar/', views.admin_campo_edit, name='admin_campo_edit'),
    
    path('gestion/estadisticas/', views.admin_estadisticas, name='admin_estadisticas'),
    
    # API
    path('api/campos/', views.api_campos_por_categoria, name='api_campos'),
    path('api/campos/dependientes/', views.api_campos_dependientes, name='api_campos_dependientes'),
]