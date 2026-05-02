# ÓPTICA PEDIDOS - Sistema de Gestión de Laboratorio

## Requisitos

- Python 3.9+
- PostgreSQL 14+
- Windows/Mac/Linux

## INSTALACIÓN

### 1. Preparar el entorno

```bash
# Crear carpeta en escritorio
cd ~/Desktop
mkdir optica_pedidos
cd optica_pedidos

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Mac/Linux
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install django psycopg2-binary python-barcode pillow reportlab
```

### 2. Configurar PostgreSQL

```sql
-- Crear base de datos
CREATE DATABASE optica_db;

-- Crear usuario
CREATE USER optica_user WITH PASSWORD 'optica123';
GRANT ALL PRIVILEGES ON DATABASE optica_db TO optica_user;
ALTER DATABASE optica_db OWNER TO optica_user;
```

### 3. Copiar proyecto

Copia la carpeta `optica_pedidos` existente o clona el repositorio.

### 4. Configurar settings

Edita `optica/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'optica_db',
        'USER': 'optica_user',
        'PASSWORD': 'optica123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Migrar y crear superusuario

```bash
cd optica_pedidos
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar servidor

```bash
python manage.py runserver
```

Abre: http://localhost:8000/login/

---

## USUARIOS DE PRUEBA

| Rol | Username | Password |
|----|----------|----------|
| ADMIN | admin | (el que crees) |
| CLIENTE | cliente1 | (el que crees) |
| SECRETARIA | secretaria1 | (el que crees) |
| LABORATORIO | laboratorio1 | (el que crees) |

---

## ROLES Y PERMISOS

### CLIENTE
- ✅ Crear pedidos
- ✅ Ver sus pedidos
- ✅ Subir imágenes
- ✅ Ver estado

### SECRETARIA
- ✅ Ver pedidos PENDIENTES
- ✅ Cambiar a RECIBIDO

### LABORATORIO
- ✅ Ver pedidos RECIBIDOS
- ✅ Cambiar a PROCESANDO

### ADMIN
- ✅ Control total
- ✅ Ver todos los pedidos
- ✅ Cambiar cualquier estado
- ✅ Generar PDF
- ✅ Configurar campos dinámicos

---

## FLUJO DE ESTADOS

```
CLIENTE → SECRETARIA → LABORATORIO → ADMIN → ADMIN
           ↓            ↓           ↓        ↓
        PENDIENTE → RECIBIDO → PROCESANDO → ENVIADO → ENTREGADO
```

No se permiten saltos de estado inválidos.

---

## FUNCIONALIDADES

### Código de Barras
- Se genera automáticamente al crear pedido
- Tipo: Code128
- Formato: PNG
- Se muestra en详情 y PDF

### Formulario Dinámico
- Admin puede crear campos en /gestion/campos/
- Tipos: texto, número, dropdown
- Dependencias entre campos

### PDF
- Genera PDF con todos los datos
- Incluye código de barras
--link: /pedidos/<id>/pdf/

### Imágenes
- Se guardan en `media/`
- Monturas, recetas, logos

---

## ESTRUCTURA DEL PROYECTO

```
optica_pedidos/
├── optica/              # Configuración Django
├── pedidos/             # App principal
│   ├── models.py        # Modelos de datos
│   ├── views.py        # Vistas
│   ├── forms.py       # Formularios
│   ├── urls.py        # Rutas
│   └── utils.py       # Utilidades (PDF, barcode)
├── templates/          # Plantillas HTML
├── static/            # CSS, JS, imágenes
└── media/            # Archivossubidos
```

---

## COMANDOS ÚTILES

```bash
# Crear migration
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recargar servidor
python manage.py runserver

# Panel admin
http://localhost:8000/admin/
```

---

## SOLUCIÓN DE PROBLEMAS

### Error de conexión a PostgreSQL
- Verificar que PostgreSQL esté ejecutándose
- Verificar credenciales en settings.py
- Crear base de datos primero

### Error de código de barras
- Instalar: `pip install python-barcode pillow`

### Error de PDF
- Instalar: `pip install reportlab`

---

## CONTACTO

Para soporte: consultael documentación o contacta al desarrollador.