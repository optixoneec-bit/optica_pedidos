# Sistema de Gestión de Pedidos - Óptica

Sistema completo para la gestión de pedidos de laboratorio óptico con trazabilidad mediante código de barras.

## Características

- ✅ Gestión de pedidos con flujo de trabajo
- ✅ Código de barras automático (Code128)
- ✅ Generación de PDF
- ✅ Formularios dinámicos configurables
- ✅ Sistema de roles y permisos
- ✅ Interfaz responsive (móvil, tablet, desktop)
- ✅ Dashboard personalizado por rol

## Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| ADMIN | Control total del sistema |
| CLIENTE | Crea y gestiona sus pedidos |
| SECRETARIA | Recibe pedidos pendientes |
| LABORATORIO | Procesa pedidos recibidos |

## Estados del Pedido

```
CLIENTE → PENDIENTE → SECRETARIA → RECIBIDO → LABORATORIO → PROCESANDO → ADMIN → ENVIADO → ENTREGADO
```

---

## Instalación

### Requisitos Previos

1. **Python 3.9+**
2. **PostgreSQL 14+**
3. **Git** (opcional)

### Paso 1: Clonar o Copiar el Proyecto

```bash
cd /Users/mackbook/Desktop/optica_pedidos
```

### Paso 2: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar PostgreSQL

1. Abrir pgAdmin o Terminal
2. Crear base de datos:

```sql
CREATE DATABASE optica_pedidos;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE optica_pedidos TO postgres;
```

3. Editar `optica/settings.py` si es necesario:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'optica_pedidos',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Paso 5: Migrar Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 6: Crear Superusuario (Admin)

```bash
python manage.py createsuperuser
```

### Paso 7: Ejecutar Servidor

```bash
python manage.py runserver
```

### Paso 8: Abrir en Navegador

```
http://localhost:8000
```

---

## Acceso

- **URL Admin**: http://localhost:8000/admin/
- **URL Login**: http://localhost:8000/login/

### Credenciales Iniciales

Después de crear el superusuario, puedes:
1. Ingresar a http://localhost:8000/admin/
2. Crear usuarios (clientes, secretaria, laboratorio)
3. Configurar campos dinámicos

---

## Estructura del Proyecto

```
optica_pedidos/
├── manage.py
├── requirements.txt
├── SPEC.md
├── README.md
├── optica/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pedidos/
│   ├── __init__.py
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── templates/
│   ├── base.html
│   └── pedidos/
│       ├── login.html
│       ├── dashboard.html
│       ├── pedido_list.html
│       ├── pedido_form.html
│       ├── pedido_detail.html
│       ├── cambiar_estado.html
│       ├── perfil.html
│       └── admin/
│           ├── usuarios.html
│           ├── usuario_form.html
│           ├── campos.html
│           ├── campo_form.html
│           └── estadisticas.html
├── static/
│   ├── css/
│   │   └── star-admin.css
│   └── js/
│       └── app.js
└── media/
    ├── barcodes/
    ├── logos/
    └── monturas/
```

---

## Comandos Útiles

### Backup de Base de Datos

```bash
pg_dump optica_pedidos > backup_$(date +%Y%m%d).sql
```

### Restaurar Backup

```bash
psql optica_pedidos < backup_20240101.sql
```

### Crear Nuevo Admin desde Terminal

```bash
python manage.py shell
```

```python
from pedidos.models import Usuario
Usuario.objects.create_superuser('admin', 'admin@optica.com', 'password123', rol='ADMIN')
```

---

## Solución de Problemas

### Error de Conexión a PostgreSQL

Verificar que PostgreSQL esté ejecutándose:
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

### Error de Permisos en Media

```bash
mkdir -p media/barcodes media/logos media/monturas
chmod -R 755 media/
```

### Instalar Pillow

```bash
pip install Pillow
```

---

## Desarrollo

### Ejecutar Tests

```bash
python manage.py test
```

### Crear Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Recargar Servidor

```bash
# Detener (Ctrl+C) y reiniciar
python manage.py runserver
```

---

## Producción

Para entorno de producción, cambiar en `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']
SECRET_KEY = 'tu-clave-secreta-muy-larga'
```

Y usar Gunicorn:

```bash
pip install gunicorn
gunicorn optica.wsgi:application --bind 0.0.0.0:8000
```

---

## Licencia

Este proyecto es propiedad del laboratorio óptico. Todos los derechos reservados.

---

## Soporte

Para soporte técnico, contactar al administrador del sistema.