"""
Pedidos App - Modelos
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import uuid


class UsuarioManager(BaseUserManager):
    """Gestor personalizado para Usuario."""
    
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es requerido')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMIN')
        return self.create_user(username, email, password, **extra_fields)


class Rol(models.TextChoices):
    """Roles del sistema."""
    ADMIN = 'ADMIN', 'Administrador'
    CLIENTE = 'CLIENTE', 'Cliente'
    SECRETARIA = 'SECRETARIA', 'Secretaria'
    LABORATORIO = 'LABORATORIO', 'Laboratorio'


class EstadoPedido(models.TextChoices):
    """Estados del pedido."""
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    RECIBIDO = 'RECIBIDO', 'Recibido'
    EN_PROCESO = 'EN_PROCESO', 'En Proceso'
    PROCESANDO = 'PROCESANDO', 'Procesando'
    PROCESADO = 'PROCESADO', 'Procesado'
    ENVIADO = 'ENVIADO', 'Enviado'
    ENTREGADO = 'ENTREGADO', 'Entregado'


class CategoriaCampo(models.TextChoices):
    """Categorías de campos."""
    LENTE = 'LENTE', 'Tipo de Lente'
    CARACTERISTICAS = 'CARACTERISTICAS', 'Características'
    MONTAJE = 'MONTAJE', 'Montaje'


class TipoCampo(models.TextChoices):
    """Tipos de campo."""
    TEXTO = 'texto', 'Texto'
    NUMERO = 'numero', 'Número'
    DROPDOWN = 'dropdown', 'Desplegable'


class TipoLente(models.TextChoices):
    """Tipos de lente."""
    MONOFOCAL = 'MONOFOCAL', 'Monofocales'
    PROGRESIVO = 'PROGRESIVO', 'Progresivos'
    ESPECIAL = 'ESPECIAL', 'Especiales'
    BIFOCAL = 'BIFOCAL', 'Bifocales'


class EstadoMontura(models.TextChoices):
    """Estado de montura."""
    NUEVA = 'NUEVA', 'Nueva'
    EN_USO = 'EN_USO', 'En uso'


class TipoBisel(models.TextChoices):
    """Tipos de bisel."""
    SIN_BISEL = 'SIN_BISEL', 'Sin bisel'
    COMPLETO = 'COMPLETO', 'Completo'
    SEMI_AIRE = 'SEMI_AIRE', 'Semi aire'
    AIRE = 'AIRE', 'Aire'


class Usuario(AbstractUser):
    """Usuario personalizado con rol y datos de óptica."""
    rol = models.CharField('Rol', max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    
    # Datos de óptica (para clientes)
    nombre_optica = models.CharField('Nombre de Óptica', max_length=200, blank=True)
    ciudad_optica = models.CharField('Ciudad', max_length=100, blank=True)
    ruc_optica = models.CharField('RUC', max_length=20, blank=True)
    vendedor_optica = models.CharField('Vendedor', max_length=100, blank=True)
    telefono_optica = models.CharField('Teléfono', max_length=20, blank=True)
    
    # Foto de logo de la óptica
    logo = models.ImageField('Logo', upload_to='logos/', blank=True, null=True)
    
    objects = UsuarioManager()
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    def es_admin(self):
        return self.rol == Rol.ADMIN
    
    def es_cliente(self):
        return self.rol == Rol.CLIENTE
    
    def es_secretaria(self):
        return self.rol == Rol.SECRETARIA
    
    def es_laboratorio(self):
        return self.rol == Rol.LABORATORIO
    
    def get_datos_optica(self):
        """Retorna los datos de la óptica del cliente."""
        return {
            'nombre': self.nombre_optica,
            'ciudad': self.ciudad_optica,
            'ruc': self.ruc_optica,
            'vendedor': self.vendedor_optica,
            'telefono': self.telefono_optica,
        }


class Campo(models.Model):
    """Campos configurables para el formulario dinámico."""
    nombre = models.CharField('Nombre', max_length=100)
    clave = models.SlugField('Clave única', max_length=50, unique=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TipoCampo.choices)
    categoria = models.CharField('Categoría', max_length=30, choices=CategoriaCampo.choices)
    requerido = models.BooleanField('Requerido', default=False)
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)
    
    # Para dropdowns
    opciones = models.JSONField('Opciones', default=list, blank=True)
    
    # Para dependencias
    depende_de = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campos_dependientes',
        verbose_name='Depende de'
    )
    valores_que_muestran = models.JSONField(
        'Valores que muestran este campo',
        default=list,
        blank=True,
        help_text='Lista de valores del campo padre que muestran este campo'
    )
    
    class Meta:
        verbose_name = 'Campo'
        verbose_name_plural = 'Campos'
        ordering = ['categoria', 'orden', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.categoria})"
    
    def tiene_opciones(self):
        return self.tipo == TipoCampo.DROPDOWN and bool(self.opciones)


class Pedido(models.Model):
    """Pedido del laboratorio óptico."""
    numero_orden = models.CharField('Número de Orden', max_length=10, unique=True, blank=True)
    uid = models.UUIDField('UID', default=uuid.uuid4, editable=False)
    
    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Cliente'
    )
    
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE
    )
    
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    # Datos de la óptica (copiados del perfil)
    nombre_optica = models.CharField('Nombre de Óptica', max_length=200)
    ciudad_optica = models.CharField('Ciudad', max_length=100)
    ruc_optica = models.CharField('RUC', max_length=20)
    vendedor_optica = models.CharField('Vendedor', max_length=100)
    telefono_optica = models.CharField('Teléfono', max_length=20)
    
    # Tipo de lente
    tipo_lente = models.CharField(
        'Tipo de Lente',
        max_length=20,
        choices=TipoLente.choices,
        blank=True
    )
    diseno_lente = models.CharField('Diseño', max_length=100, blank=True)
    
    # Material
    material = models.CharField('Material', max_length=20, blank=True)
    
    # Tratamientos
    tratamiento_fotosensible = models.CharField('Fotosensible', max_length=20, blank=True)
    tratamiento_antireflejo = models.CharField('Antireflejo', max_length=20, blank=True)
    tratamiento_filtro_azul = models.BooleanField('Filtro Luz Azul', default=False)
    tratamiento_transitions = models.BooleanField('Transitions', default=False)
    
    # Receta - Ojo Derecho
    od_esfera = models.CharField('OD Esfera', max_length=10, blank=True)
    od_cilindro = models.CharField('OD Cilindro', max_length=10, blank=True)
    od_eje = models.CharField('OD Eje', max_length=10, blank=True)
    od_dnp = models.CharField('OD DNP', max_length=10, blank=True)
    od_altura = models.CharField('OD Altura', max_length=10, blank=True)
    od_adicion = models.CharField('OD Adición', max_length=10, blank=True)
    
    # Receta - Ojo Izquierdo
    oi_esfera = models.CharField('OI Esfera', max_length=10, blank=True)
    oi_cilindro = models.CharField('OI Cilindro', max_length=10, blank=True)
    oi_eje = models.CharField('OI Eje', max_length=10, blank=True)
    oi_dnp = models.CharField('OI DNP', max_length=10, blank=True)
    oi_altura = models.CharField('OI Altura', max_length=10, blank=True)
    oi_adicion = models.CharField('OI Adición', max_length=10, blank=True)
    
    # Extras receta
    horizontal = models.CharField('Horizontal', max_length=10, blank=True)
    vertical = models.CharField('Vertical', max_length=10, blank=True)
    puente = models.CharField('Puente', max_length=10, blank=True)
    distancia_mecanica = models.CharField('Distancia Mecánica', max_length=10, blank=True)
    
    # Montura
    montura_descripcion = models.CharField('Descripción Montura', max_length=200, blank=True)
    montura_estado = models.CharField(
        'Estado Montura',
        max_length=20,
        choices=EstadoMontura.choices,
        blank=True
    )
    montura_foto = models.ImageField('Foto Montura', upload_to='monturas/', blank=True, null=True)
    
    # Bisel
    tipo_bisel = models.CharField(
        'Tipo de Bisel',
        max_length=20,
        choices=TipoBisel.choices,
        blank=True
    )
    
    # Observaciones
    observaciones = models.TextField('Observaciones', blank=True)
    
    # Código de barras
    barcode = models.ImageField(
        'Código de Barras',
        upload_to='barcodes/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido {self.numero_orden}"
    
    def save(self, *args, **kwargs):
        if not self.numero_orden:
            self.numero_orden = self.generar_numero_orden()
        super().save(*args, **kwargs)
    
    def generar_numero_orden(self):
        """Genera el siguiente número de orden secuencial."""
        ultimo = Pedido.objects.order_by('id').last()
        if ultimo:
            ultimo_numero = int(ultimo.numero_orden)
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        return f"{nuevo_numero:06d}"
    
    def copiar_datos_optica(self):
        """Copia los datos de la óptica del cliente."""
        datos = self.cliente.get_datos_optica()
        self.nombre_optica = datos['nombre']
        self.ciudad_optica = datos['ciudad']
        self.ruc_optica = datos['ruc']
        self.vendedor_optica = datos['vendedor']
        self.telefono_optica = datos.get('telefono', '')
    
    def get_estado_siguiente(self):
        """Retorna el siguiente estado válido."""
        flujo = {
            EstadoPedido.PENDIENTE: EstadoPedido.RECIBIDO,
            EstadoPedido.RECIBIDO: EstadoPedido.EN_PROCESO,
            EstadoPedido.EN_PROCESO: EstadoPedido.PROCESANDO,
            EstadoPedido.PROCESANDO: EstadoPedido.PROCESADO,
            EstadoPedido.PROCESADO: EstadoPedido.ENVIADO,
            EstadoPedido.ENVIADO: EstadoPedido.ENTREGADO,
        }
        return flujo.get(self.estado)
    
    def puede_cambiar_estado(self, usuario):
        """Verifica si el usuario puede cambiar el estado."""
        if usuario.es_admin():
            return True
        
        roles_permitidos = {
            EstadoPedido.PENDIENTE: [Rol.SECRETARIA, Rol.ADMIN],
            EstadoPedido.RECIBIDO: [Rol.SECRETARIA, Rol.ADMIN],  # Secretaria envía a proceso
            EstadoPedido.EN_PROCESO: [Rol.LABORATORIO, Rol.ADMIN],  # Laboratorio recibe
            EstadoPedido.PROCESANDO: [Rol.LABORATORIO, Rol.ADMIN],  # Laboratorio procesa
            EstadoPedido.PROCESADO: [Rol.SECRETARIA, Rol.ADMIN],  # Secretaria entrega
            EstadoPedido.ENVIADO: [Rol.SECRETARIA, Rol.ADMIN],  # Secretaria entrega al cliente
        }
        
        return usuario.rol in roles_permitidos.get(self.estado, [])


class PedidoValor(models.Model):
    """Valores dinámicos para campos personalizados."""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='valores'
    )
    campo = models.ForeignKey(
        Campo,
        on_delete=models.PROTECT,
        related_name='valores'
    )
    valor = models.JSONField('Valor')
    
    class Meta:
        verbose_name = 'Valor de Campo'
        verbose_name_plural = 'Valores de Campos'
        unique_together = ['pedido', 'campo']
    
    def __str__(self):
        return f"{self.pedido} - {self.campo}: {self.valor}"


def generar_barcode(pedido):
    """Genera el código de barras para un pedido."""
    import barcode
    from barcode.writer import ImageWriter
    from django.conf import settings
    import os
    
    # Crear directorio si no existe
    barcode_dir = settings.MEDIA_ROOT / 'barcodes'
    os.makedirs(barcode_dir, exist_ok=True)
    
    # Generar código
    codigo = pedido.numero_orden
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(codigo, writer=ImageWriter())
    
    # Guardar
    ruta = barcode_dir / codigo
    barcode_instance.save(str(ruta))
    
    return f'barcodes/{codigo}.png'