# Script para modificar views.py
with open('pedidos/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar el texto exacto
old = """    # Cambiar el estado
    pedido.estado = siguiente
    pedido.save()

    messages.success(request, f'Pedido {pedido.numero_orden} cambiado a {pedido.get_estado_display()}')
    return redirect('pedido_detail', pk=pk)


@login_required
def pedido_pdf(request, pk):"""

new = """    # Cambiar el estado
    pedido.estado = siguiente
    pedido.save()

    # Si es LABORATORIO y cambió de EN_PROCESO a PROCESANDO, crear archivo de control
    if usuario.es_laboratorio() and pedido.estado == EstadoPedido.PROCESANDO:
        import os
        from pathlib import Path
        
        archivos_dir = Path('C:/Users/Administrator/Desktop/Archivos')
        os.makedirs(archivos_dir, exist_ok=True)
        
        nombre_archivo = f'{pedido.numero_orden}.txt'
        ruta_archivo = archivos_dir / nombre_archivo
        
        with open(ruta_archivo, 'w') as f:
            f.write('')
        
        messages.success(request, f'Pedido {pedido.numero_orden} cambiado a {pedido.get_estado_display()} - Archivo creado')
    else:
        messages.success(request, f'Pedido {pedido.numero_orden} cambiado a {pedido.get_estado_display()}')
    
    return redirect('pedido_detail', pk=pk)


@login_required
def pedido_pdf(request, pk):"""

if old in content:
    content = content.replace(old, new)
    with open('pedidos/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('MODIFICADO OK')
else:
    print('NO ENCONTRADO')
    # Buscar la línea
    if 'pedido.save()' in content:
        print('pedido.save() encontrado')