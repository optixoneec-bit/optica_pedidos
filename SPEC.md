# Sistema de Gestión de Pedidos - Óptica

## Concepto y Visión

Sistema empresarial completo para laboratorio óptico con trazabilidad mediante código de barras. Flujo de trabajo lineal que garantiza control total desde la creación del pedido hasta la entrega, con roles especializados y formularios dinámicos configurables por el administrador.

## Stack Tecnológico

- **Backend**: Django 4.2+ (Python)
- **Base de datos**: PostgreSQL 14+
- **Frontend**: Bootstrap 5 + Star Admin
- **Barcode**: python-barcode (Code128)
- **PDF**: ReportLab / WeasyPrint
- **JavaScript**: Vanilla ES6+ (sin frameworks adicionales)

## Modelos de Datos

### Usuario (User)
- Extiende Django User con roles: ADMIN, CLIENTE, SECRETARIA, LABORATORIO
- Cliente asociado a datos de óptica (nombre, ciudad, RUC, vendedor)

### Campo (Configuración Dinámica)
- nombre, tipo (texto/número/dropdown), opciones, requerido, orden, categoría

### Pedido
- número_orden (único, autoincremental format 000001)
- cliente (FK)
- estado (PENDIENTE/RECIBIDO/PROCESANDO/ENVIADO/ENTREGADO)
- barcode (imagen PNG)
- fecha_creacion, fecha_actualizacion
- Secciones: DatosÓptica, Lente, Características, Receta, Montura, Bisel, Observaciones

### PedidoValor
- pedido (FK), campo (FK), valor

## Flujo de Estados

```
CLIENTE → PENDIENTE
SECRETARIA → RECIBIDO
LABORATORIO → PROCESANDO
ADMIN → ENVIADO → ENTREGADO
```

## Permisos por Rol

| Acción | ADMIN | CLIENTE | SECRETARIA | LABORATORIO |
|--------|-------|---------|------------|-------------|
| Crear pedido | ✓ | ✓ | ✗ | ✗ |
| Ver propios | ✓ | ✓ | ✗ | ✗ |
| Ver todos | ✓ | ✗ | ✓ | ✓ |
| Cambiar estado | ✓ | ✗ | ✓ | ✓ |
| Configurar campos | ✓ | ✗ | ✗ | ✗ |
| Generar PDF | ✓ | ✓ | ✓ | ✓ |

## Código de Barras

- Tipo: CODE128
- Basado en número de orden (000001)
- Generado al crear pedido
- Almacenado como PNG en media/
- Incluido en PDF

## Secciones del Formulario

1. **Datos Óptica**: Auto-completado desde perfil cliente
2. **Tipo Lente**: Dropdown dinámico con dependiente "Diseño"
3. **Características**: Material, filtros, antirreflejo
4. **Receta**: Ojo derecho/izquierdo con todas las métricas
5. **Montura**: Descripción + foto
6. **Bisel**: Opciones predefinidas
7. **Observaciones**: Texto libre

## Dashboards

- **Cliente**: Lista de sus pedidos, crear nuevo
- **Secretaria**: Pedidos pendientes, botón Recibido
- **Laboratorio**: Pedidos recibidos, botón Procesando
- **Admin**: Vista global, configuración, CRUD completo