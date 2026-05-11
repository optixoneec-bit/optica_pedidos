import re

f = open('pedidos/views.py', 'r', encoding='utf-8', errors='replace')
c = f.read()
f.close()

# Find the function
m = re.search(r'def pedido_avanzar_estado', c)
if m:
    print('Found function at position:', m.start())
    # Find the target lines within next 2000 chars
    section = c[m.start():m.start()+2000]
    
    # Find pedido.save() followed by messages.success
    target = re.search(r'pedido\.save\(\).*?messages\.success', section, re.DOTALL)
    if target:
        print('Found target section')
        print('Text:', repr(target.group()[:150]))
        
        # Replace
        old_text = "pedido.estado = siguiente\n        pedido.save()\n\n        messages.success(request, f'Pedido {pedido.numero_orden} cambiado a {pedido.get_estado_display()}')"
        
        new_text = """pedido.estado = siguiente
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
            messages.success(request, f'Pedido {pedido.numero_orden} cambiado a {pedido.get_estado_display()}')"""
        
        if old_text in section:
            c = c.replace(old_text, new_text, 1)
            f = open('pedidos/views.py', 'w', encoding='utf-8')
            f.write(c)
            f.close()
            print('MODIFIED OK')
        else:
            print('OLD TEXT NOT FOUND')
            print('Looking for:', repr(old_text[:50]))
    else:
        print('Target section not found')
else:
    print('Function not found')