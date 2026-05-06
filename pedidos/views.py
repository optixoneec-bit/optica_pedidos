"""
Pedidos App - Vistas
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    Usuario, Pedido, Campo, PedidoValor,
    EstadoPedido, Rol, TipoCampo, CategoriaCampo
)
from .forms import LoginForm, UsuarioForm, UsuarioEditForm, PedidoForm, CampoForm, PerfilForm, CambioEstadoForm
from .utils import generar_barcode_pdf, crear_pdf_pedido
import json


def login_view(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            from django.contrib.auth import authenticate
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('dashboard')
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'pedidos/login.html', {'form': form})


def logout_view(request):
    """Vista de cierre de sesión."""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard principal según el rol del usuario."""
    usuario = request.user
    
    if usuario.es_admin():
        # Admin ve todos los pedidos
        pedidos = Pedido.objects.all().order_by('-fecha_creacion')
        rol = 'admin'
        contexto = {
            'total_pedidos': Pedido.objects.count(),
            'pedidos_pendientes': Pedido.objects.filter(estado=EstadoPedido.PENDIENTE).count(),
            'pedidos_recibidos': Pedido.objects.filter(estado=EstadoPedido.RECIBIDO).count(),
            'pedidos_procesando': Pedido.objects.filter(estado=EstadoPedido.PROCESANDO).count(),
            'pedidos_enviados': Pedido.objects.filter(estado=EstadoPedido.ENVIADO).count(),
            'pedidos_entregados': Pedido.objects.filter(estado=EstadoPedido.ENTREGADO).count(),
            'usuario': usuario,
            'usuario_rol': rol,
        }
    elif usuario.es_secretaria():
        # Secretaria ve todos los pedidos (puede filtrar por estado)
        pedidos = Pedido.objects.all().order_by('-fecha_creacion')
        rol = 'secretaria'
        contexto = {'usuario': usuario, 'usuario_rol': rol}
    elif usuario.es_laboratorio():
        # Laboratorio ve todos los pedidos (puede filtrar por estado)
        pedidos = Pedido.objects.all().order_by('-fecha_creacion')
        rol = 'laboratorio'
        contexto = {'usuario': usuario, 'usuario_rol': rol}
    else:
        # Cliente ve solo sus pedidos
        pedidos = Pedido.objects.filter(cliente=usuario).order_by('-fecha_creacion')
        rol = 'cliente'
        contexto = {'usuario': usuario, 'usuario_rol': rol}
    
    # Paginación
    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto['page_obj'] = page_obj
    contexto['pedidos'] = page_obj
    
    return render(request, 'pedidos/dashboard.html', contexto)


@login_required
def pedido_list(request):
    """Lista de pedidos con filtros."""
    usuario = request.user
    pedidos = Pedido.objects.all()
    
    # Filtros
    estado = request.GET.get('estado')
    busqueda = request.GET.get('q')
    
    if usuario.es_cliente():
        pedidos = pedidos.filter(cliente=usuario)
    elif estado:
        pedidos = pedidos.filter(estado=estado)
    
    if busqueda:
        pedidos = pedidos.filter(
            Q(numero_orden__icontains=busqueda) |
            Q(nombre_optica__icontains=busqueda) |
            Q(cliente__nombre_optica__icontains=busqueda)
        )
    
    pedidos = pedidos.order_by('-fecha_creacion')
    
    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    contexto = {
        'page_obj': page_obj,
        'pedidos': page_obj,
        'estados': EstadoPedido.choices,
        'estado_filtro': estado,
        'busqueda': busqueda,
        'usuario': usuario,
    }
    
    return render(request, 'pedidos/pedido_list.html', contexto)


@login_required
def pedido_create(request):
    """Crear nuevo pedido."""
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        
        # Procesar campos dinámicos
        campos_valores = {}
        for key, value in request.POST.items():
            if key.startswith('campo_'):
                campo_id = key.replace('campo_', '')
                try:
                    campo = Campo.objects.get(id=campo_id)
                    campos_valores[campo_id] = value
                except Campo.DoesNotExist:
                    pass
        
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user
            pedido.copiar_datos_optica()
            pedido.save()
            
            # Guardar valores de campos dinámicos
            for campo_id, valor in campos_valores.items():
                try:
                    campo = Campo.objects.get(id=campo_id)
                    PedidoValor.objects.update_or_create(
                        pedido=pedido,
                        campo=campo,
                        defaults={'valor': valor}
                    )
                except Campo.DoesNotExist:
                    pass
            
            # Generar código de barras
            from .utils import generar_barcode
            barcode_path = generar_barcode(pedido)
            pedido.barcode = barcode_path
            pedido.save()
            
            messages.success(request, f'Pedido {pedido.numero_orden} creado exitosamente.')
            return redirect('pedido_detail', pk=pedido.pk)
    else:
        form = PedidoForm()
    
    # Obtener campos dinámicos
    campos_lente = Campo.objects.filter(categoria=CategoriaCampo.LENTE, activo=True)
    campos_caracteristicas = Campo.objects.filter(categoria=CategoriaCampo.CARACTERISTICAS, activo=True)
    campos_montaje = Campo.objects.filter(categoria=CategoriaCampo.MONTAJE, activo=True)
    
    # Crear diccionario de opciones dinámico
    opciones_dinamicas = {}
    for campo in list(campos_lente) + list(campos_caracteristicas) + list(campos_montaje):
        if campo.opciones:
            opciones_dinamicas[campo.clave] = campo.opciones
    
    # Crear diccionario de tipos de campo
    tipos_campo = {}
    for campo in list(campos_lente) + list(campos_caracteristicas) + list(campos_montaje):
        tipos_campo[campo.clave] = campo.tipo
    
    import json
    from types import SimpleNamespace
    
    # Objeto vacío para el template
    pedido_vacio = SimpleNamespace(
        id='',
        # Datos óptica
        nombre_optica='', ciudad_optica='', ruc_optica='', vendedor_optica='', telefono_optica='',
        # Tipo lente
        tipo_lente='', diseno_lente='',
        # Material
        material='',
        # Tratamientos
        tratamiento_fotosensible='', tratamiento_antireflejo='', tratamiento_filtro_azul='', tratamiento_transitions='',
        # Receta OD
        od_esfera='', od_cilindro='', od_eje='', od_dnp='', od_altura='', od_adicion='',
        # Receta OI
        oi_esfera='', oi_cilindro='', oi_eje='', oi_dnp='', oi_altura='', oi_adicion='',
        # Extras
        horizontal='', vertical='', puente='', distancia_mecanica='',
        # Montura
        montura_descripcion='', montura_estado='', montura_foto='',
        # Bisel
        tipo_bisel='',
        # Observaciones
        observaciones='',
    )
    
    # Opciones para JS - formato opciones_js
    opciones_js = json.dumps(opciones_dinamicas)
    
    contexto = {
        'form': form,
        'pedido': pedido_vacio,
        'campos_lente': campos_lente,
        'campos_caracteristicas': campos_caracteristicas,
        'campos_montaje': campos_montaje,
        'datos_optica': request.user.get_datos_optica(),
        'usuario': request.user,
        'opciones_js': opciones_js,
        'tipos_campo': json.dumps(tipos_campo),
    }
    
    return render(request, 'pedidos/pedido_form.html', contexto)


@login_required
def pedido_detail(request, pk):
    """Ver detalle de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    usuario = request.user
    
    # Verificar permisos
    if usuario.es_cliente() and pedido.cliente != usuario:
        messages.error(request, 'No tienes permisos para ver este pedido.')
        return redirect('dashboard')
    
    # Obtener valores dinámicos
    valores_dinamicos = {}
    for valor in pedido.valores.all():
        valores_dinamicos[valor.campo.id] = valor.valor
    
    contexto = {
        'pedido': pedido,
        'valores_dinamicos': valores_dinamicos,
        'usuario': usuario,
        'puede_cambiar_estado': pedido.puede_cambiar_estado(usuario)
    }
    
    return render(request, 'pedidos/pedido_detail.html', contexto)


@login_required
def pedido_update(request, pk):
    """Editar un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    usuario = request.user
    
    # Verificar permisos
    if usuario.es_cliente() and pedido.cliente != usuario:
        messages.error(request, 'No tienes permisos para editar este pedido.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pedido {pedido.numero_orden} actualizado.')
            return redirect('pedido_detail', pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)
    
    contexto = {'form': form, 'pedido': pedido}
    return render(request, 'pedidos/pedido_form.html', contexto)


@login_required
def pedido_cambiar_estado(request, pk):
    """Cambiar el estado de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    usuario = request.user
    
    if not pedido.puede_cambiar_estado(usuario):
        messages.error(request, 'No tienes permisos para cambiar el estado de este pedido.')
        return redirect('pedido_detail', pk=pk)
    
    if request.method == 'POST':
        form = CambioEstadoForm(request.POST)
        if form.is_valid():
            nuevo_estado = form.cleaned_data['nuevo_estado']
            observaciones = form.cleaned_data['observaciones']
            
            # Verificar transición válida
            estado_siguiente = pedido.get_estado_siguiente()
            if nuevo_estado != estado_siguiente and not usuario.es_admin():
                messages.error(request, 'Transición de estado no válida.')
                return redirect('pedido_detail', pk=pk)
            
            pedido.estado = nuevo_estado
            if observaciones:
                pedido.observaciones += f"\n\n[Estado: {nuevo_estado}] {observaciones}"
            pedido.save()
            
            messages.success(request, f'Pedido {pedido.numero_orden} actualizado a {pedido.get_estado_display()}')
            return redirect('pedido_detail', pk=pk)
    else:
        form = CambioEstadoForm(initial={'nuevo_estado': pedido.get_estado_siguiente()})
    
    contexto = {'form': form, 'pedido': pedido}
    return render(request, 'pedidos/cambiar_estado.html', contexto)


@login_required
def pedido_avanzar_estado(request, pk):
    """Avanza el estado del pedido al siguiente automáticamente."""
    pedido = get_object_or_404(Pedido, pk=pk)
    usuario = request.user
    
    if not pedido.puede_cambiar_estado(usuario):
        messages.error(request, 'No tienes permisos para cambiar el estado de este pedido.')
        return redirect('pedido_detail', pk=pk)
    
    # Obtener el siguiente estado
    siguiente = pedido.get_estado_siguiente()
    if not siguiente:
        messages.error(request, 'No hay siguiente estado disponible.')
        return redirect('pedido_detail', pk=pk)
    
    # Verificar que la transición sea válida para el rol
    if usuario.es_cliente():
        messages.error(request, 'Los clientes no pueden cambiar el estado.')
        return redirect('pedido_detail', pk=pk)
    
    # Verificaciones por rol (secretaria tiene dos acciones)
    if usuario.es_secretaria():
        if pedido.estado == EstadoPedido.PENDIENTE:
            pass  # Puede cambiar a RECIBIDO
        elif pedido.estado == EstadoPedido.RECIBIDO:
            pass  # Puede cambiar a EN_PROCESO
        elif pedido.estado == EstadoPedido.PROCESADO:
            pass  # Puede cambiar a ENVIADO
        elif pedido.estado == EstadoPedido.ENVIADO:
            pass  # Puede cambiar a ENTREGADO
        else:
            messages.error(request, 'La secretaria no puede cambiar este estado.')
            return redirect('pedido_detail', pk=pk)
    
    if usuario.es_laboratorio():
        if pedido.estado == EstadoPedido.EN_PROCESO:
            pass  # Puede cambiar a PROCESANDO
        elif pedido.estado == EstadoPedido.PROCESANDO:
            pass  # Puede cambiar a PROCESADO
        else:
            messages.error(request, 'El laboratorio no puede cambiar este estado.')
            return redirect('pedido_detail', pk=pk)
    
    # Cambiar el estado
    pedido.estado = siguiente
    pedido.save()
    
    messages.success(request, f'Pedido {pedido.numero_orden} cambiado a {pedido.get_estado_display()}')
    return redirect('pedido_detail', pk=pk)


@login_required
def pedido_pdf(request, pk):
    """Generar PDF de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    usuario = request.user
    
    if usuario.es_cliente() and pedido.cliente != usuario:
        return HttpResponse('No tienes permisos', status=403)
    
    pdf_response = crear_pdf_pedido(pedido)
    return pdf_response


@login_required
def pedido_eliminar(request, pk):
    """Eliminar un pedido (solo admin)."""
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para eliminar pedidos.')
        return redirect('dashboard')
    
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        numero = pedido.numero_orden
        pedido.delete()
        messages.success(request, f'Pedido {numero} eliminado.')
        return redirect('pedido_list')
    
    return render(request, 'pedidos/admin/usuario_confirm_delete.html', {
        'pedido': pedido,
        'object': pedido,
        'usuario': request.user,
        'titulo': 'Eliminar Pedido',
        'mensaje': f'¿Estás seguro de eliminar el pedido "{pedido.numero_orden}"? Esta acción no se puede deshacer.'
    })


# Vistas para Admin
@login_required
def admin_usuarios(request):
    """Lista de usuarios (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    usuarios = Usuario.objects.all().order_by('-date_joined')
    paginator = Paginator(usuarios, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    contexto = {'page_obj': page_obj, 'usuarios': page_obj, 'usuario': request.user}
    return render(request, 'pedidos/admin/usuarios.html', contexto)


@login_required
def admin_usuario_create(request):
    """Crear usuario (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
                return redirect('admin_usuarios')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
        else:
            messages.error(request, f'Formulario inválido: {form.errors}')
    else:
        form = UsuarioForm()
    
    return render(request, 'pedidos/admin/usuario_form.html', {
        'form': form,
        'usuario': request.user,
        'es_nuevo': True
    })


@login_required
def admin_usuario_edit(request, pk):
    """Editar usuario (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    print(f"EDICIÓN - Usuario: {usuario.username}, es_nuevo debería ser False")
    
    if request.method == 'POST':
        # Remover campos de contraseña del POST para edición
        post_data = request.POST.copy()
        post_data.pop('password1', None)
        post_data.pop('password2', None)
        
        form = UsuarioEditForm(post_data, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('admin_usuarios')
        else:
            print(f"Errores: {form.errors}")
            messages.error(request, f'Error en el formulario: {form.errors}')
    else:
        form = UsuarioEditForm(instance=usuario)
    
    return render(request, 'pedidos/admin/usuario_form.html', {
        'form': form,
        'usuario': usuario,
        'es_nuevo': False
    })


@login_required
def admin_usuario_delete(request, pk):
    """Eliminar usuario (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir eliminarse a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('admin_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        pedido_count = Pedido.objects.filter(cliente=usuario).count()
        
        if pedido_count > 0:
            messages.error(request, f'No se puede eliminar. El usuario tiene {pedido_count} pedido(s) asociado(s). Primero elimine los pedidos.')
            return redirect('admin_usuarios')
        
        try:
            usuario.delete()
            messages.success(request, f'Usuario "{username}" eliminado.')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
        return redirect('admin_usuarios')
    
    return render(request, 'pedidos/admin/usuario_confirm_delete.html', {
        'usuario': usuario,
        'titulo': 'Eliminar Usuario',
        'mensaje': f'¿Estás seguro de eliminar el usuario "{usuario.username}"? Esta acción no se puede deshacer.'
    })


@login_required
def admin_pedido_delete(request, pk):
    """Eliminar pedido (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        numero = pedido.numero_orden
        pedido.delete()
        messages.success(request, f'Pedido "{numero}" eliminado.')
        return redirect('pedido_list')
    
    return render(request, 'pedidos/admin/usuario_confirm_delete.html', {
        'object': pedido,
        'usuario': request.user,
        'titulo': 'Eliminar Pedido',
        'mensaje': f'¿Estás seguro de eliminar el pedido "{pedido.numero_orden}"? Esta acción no se puede deshacer.'
    })


@login_required
def admin_campos(request):
    """Configurar campos dinámicos (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    campos = Campo.objects.all().order_by('categoria', 'orden')
    campos_lente = campos.filter(categoria=CategoriaCampo.LENTE)
    campos_caracteristicas = campos.filter(categoria=CategoriaCampo.CARACTERISTICAS)
    campos_montaje = campos.filter(categoria=CategoriaCampo.MONTAJE)
    
    contexto = {
        'campos': campos,
        'campos_lente': campos_lente,
        'campos_caracteristicas': campos_caracteristicas,
        'campos_montaje': campos_montaje,
        'usuario': request.user,
    }
    return render(request, 'pedidos/admin/campos.html', contexto)


@login_required
def admin_campo_create(request):
    """Crear campo dinámico (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CampoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo creado exitosamente.')
            return redirect('admin_campos')
    else:
        form = CampoForm()
    
    campos_disponibles = Campo.objects.filter(tipo=TipoCampo.DROPDOWN)
    
    # Objeto campo vacío para el template
    campo_vacio = type('Campo', (), {
        'nombre': '', 'clave': '', 'tipo': '', 'categoria': '',
        'requerido': False, 'orden': 0, 'activo': True, 'opciones': [],
        'depende_de': None, 'valores_que_muestran': []
    })()
    
    return render(request, 'pedidos/admin/campo_form.html', {
        'form': form,
        'campo': campo_vacio,
        'campos_disponibles': campos_disponibles,
        'usuario': request.user,
    })


@login_required
def admin_campo_edit(request, pk):
    """Editar campo dinámico (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    campo = get_object_or_404(Campo, pk=pk)
    
    if request.method == 'POST':
        form = CampoForm(request.POST, instance=campo)
        if form.is_valid():
            campo = form.save()
            messages.success(request, 'Campo actualizado')
            return redirect('admin_campos')
    else:
        form = CampoForm(instance=campo)
    
    campos_disponibles = Campo.objects.filter(tipo=TipoCampo.DROPDOWN)
    
    return render(request, 'pedidos/admin/campo_form.html', {
        'form': form,
        'campo': campo,
        'campos_disponibles': campos_disponibles,
        'usuario': request.user,
    })


@login_required
def admin_estadisticas(request):
    """Estadísticas (solo admin)."""
    if not request.user.es_admin():
        return redirect('dashboard')
    
    contexto = {
        'total_pedidos': Pedido.objects.count(),
        'pedidos_pendientes': Pedido.objects.filter(estado=EstadoPedido.PENDIENTE).count(),
        'pedidos_recibidos': Pedido.objects.filter(estado=EstadoPedido.RECIBIDO).count(),
        'pedidos_procesando': Pedido.objects.filter(estado=EstadoPedido.PROCESANDO).count(),
        'pedidos_enviados': Pedido.objects.filter(estado=EstadoPedido.ENVIADO).count(),
        'pedidos_entregados': Pedido.objects.filter(estado=EstadoPedido.ENTREGADO).count(),
        'total_clientes': Usuario.objects.filter(rol=Rol.CLIENTE).count(),
        'total_usuarios': Usuario.objects.count(),
        'usuario': request.user,
    }
    
    return render(request, 'pedidos/admin/estadisticas.html', contexto)


@login_required
def perfil(request):
    """Perfil del usuario."""
    usuario = request.user
    
    if request.method == 'POST':
        # Solo el admin puede editar
        if not usuario.es_admin:
            messages.error(request, 'Solo el administrador puede editar estos datos.')
            return redirect('perfil')
        
        form = PerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=usuario)
    
    contexto = {'form': form, 'usuario': usuario}
    return render(request, 'pedidos/perfil.html', contexto)


# API para campos dinámicos
@login_required
def api_campos_por_categoria(request):
    """API que devuelve campos según categoría."""
    categoria = request.GET.get('categoria')
    
    if categoria:
        campos = Campo.objects.filter(categoria=categoria, activo=True)
    else:
        campos = Campo.objects.filter(activo=True)
    
    datos = []
    for campo in campos:
        datos.append({
            'id': campo.id,
            'nombre': campo.nombre,
            'clave': campo.clave,
            'tipo': campo.tipo,
            'requerido': campo.requerido,
            'opciones': campo.opciones if campo.tipo == TipoCampo.DROPDOWN else []
        })
    
    return JsonResponse({'campos': datos})


@login_required
def api_campos_dependientes(request):
    """API que devuelve campos que dependen de otro."""
    campo_id = request.GET.get('campo_id')
    valor_seleccionado = request.GET.get('valor')
    
    if not campo_id:
        return JsonResponse({'campos': []})
    
    try:
        campo = Campo.objects.get(id=campo_id)
        campos = Campo.objects.filter(
            depende_de=campo,
            valores_que_muestran__contains=[valor_seleccionado]
        )
    except Campo.DoesNotExist:
        campos = []
    
    datos = []
    for campo in campos:
        datos.append({
            'id': campo.id,
            'nombre': campo.nombre,
            'clave': campo.clave,
            'tipo': campo.tipo,
            'opciones': campo.opciones if campo.tipo == TipoCampo.DROPDOWN else []
        })
    
    return JsonResponse({'campos': datos})