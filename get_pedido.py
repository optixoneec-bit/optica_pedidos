import os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica.settings')

import django
django.setup()

from pedidos.models import Pedido
p = Pedido.objects.get(numero_orden='000007')

print('=== DATOS DEL PEDIDO 000007 ===')
print('CLIENT:', p.nombre_optica)
print('CLINIT:', p.vendedor_optica)
print('SPH OD:', p.od_esfera)
print('SPH OI:', p.oi_esfera)
print('CYL OD:', p.od_cilindro)
print('CYL OI:', p.oi_cilindro)
print('AX OD:', p.od_eje)
print('AX OI:', p.oi_eje)
print('ADD OD:', p.od_adicion)
print('ADD OI:', p.oi_adicion)
print('DBL:', p.puente)
print('IPD OD:', p.od_dnp)
print('IPD OI:', p.oi_dnp)
print('HBOX:', p.horizontal)
print('VBOX:', p.vertical)
print('FRAM:', p.montura_descripcion)
print('SEGHT OD:', p.od_altura)
print('SEGHT OI:', p.oi_altura)
print('FTYP:', p.tipo_bisel)
print('MATERIAL:', p.material)
print('TIPO_LENTE:', p.tipo_lente)
print('DISENO:', p.diseno_lente)
print('MONTURA_ESTADO:', p.montura_estado)