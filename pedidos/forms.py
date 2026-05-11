"""
Pedidos App - Formularios
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Usuario, Pedido, Campo, PedidoValor,
    TipoCampo, EstadoPedido, EstadoMontura, TipoBisel
)


class LoginForm(forms.Form):
    """Formulario de inicio de sesión."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class UsuarioForm(UserCreationForm):
    """Formulario para crear usuarios."""
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label='Usuario activo'
    )
    rol = forms.ChoiceField(
        choices=Usuario._meta.get_field('rol').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Rol'
    )
    
    nombre_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Nombre de Óptica'
    )
    ciudad_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Ciudad'
    )
    ruc_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='RUC'
    )
    vendedor_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Vendedor'
    )
    telefono_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Teléfono'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'rol',
            'nombre_optica', 'ciudad_optica', 'ruc_optica',
            'vendedor_optica', 'telefono_optica'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UsuarioEditForm(forms.ModelForm):
    """Formulario para editar usuarios."""
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}),
        required=False,
        label='Nueva contraseña'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        required=False,
        label='Confirmar contraseña'
    )
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label='Usuario activo'
    )
    rol = forms.ChoiceField(
        choices=Usuario._meta.get_field('rol').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Rol'
    )
    
    nombre_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Nombre de Óptica'
    )
    ciudad_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Ciudad'
    )
    ruc_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='RUC'
    )
    vendedor_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Vendedor'
    )
    telefono_optica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Teléfono'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name', 'rol',
            'nombre_optica', 'ciudad_optica', 'ruc_optica',
            'vendedor_optica', 'telefono_optica', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.original_username = None
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.original_username = self.instance.username
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username != self.original_username:
            # Check if new username is taken
            if Usuario.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un usuario con este nombre.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(password1) < 6:
                raise forms.ValidationError('La contraseña debe tener al menos 6 caracteres.')
        
        return cleaned_data

    def save(self, commit=True):
        # Obtener la contraseña nueva si existe
        password1 = self.cleaned_data.get('password1')
        
        # Si hay contraseña nueva, encriptarla ANTES de guardar
        if password1 and self.instance.pk:
            self.instance.set_password(password1)
        
        # Guardar el usuario con todos los datos del formulario
        usuario = super().save(commit=commit)
        
        return usuario


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil propio."""
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'nombre_optica', 'ciudad_optica', 'ruc_optica',
            'vendedor_optica', 'telefono_optica', 'logo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombre_optica': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_optica': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc_optica': forms.TextInput(attrs={'class': 'form-control'}),
            'vendedor_optica': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_optica': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PedidoForm(forms.ModelForm):
    """Formulario para crear/editar pedidos."""
    
    # Tipo de lente
    tipo_lente = forms.ChoiceField(
        choices=Pedido._meta.get_field('tipo_lente').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Tipo de Lente'
    )
    diseno_lente = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Diseño'
    )
    
    # Material
    material = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Material'
    )
    indice = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1.50'}),
        required=False,
        label='Índice'
    )
    
    # Ojo Derecho
    od_esfera = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OD Esfera'}),
        required=False, label='OD Esfera'
    )
    od_cilindro = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OD Cilindro'}),
        required=False, label='OD Cilindro'
    )
    od_eje = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OD Eje'}),
        required=False, label='OD Eje'
    )
    od_dnp = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OD DNP'}),
        required=False, label='OD DNP'
    )
    od_altura = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OD Altura'}),
        required=False, label='OD Altura'
    )
    od_adicion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OD Adición'}),
        required=False, label='OD Adición'
    )
    
    # Ojo Izquierdo
    oi_esfera = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OI Esfera'}),
        required=False, label='OI Esfera'
    )
    oi_cilindro = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OI Cilindro'}),
        required=False, label='OI Cilindro'
    )
    oi_eje = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OI Eje'}),
        required=False, label='OI Eje'
    )
    oi_dnp = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OI DNP'}),
        required=False, label='OI DNP'
    )
    oi_altura = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OI Altura'}),
        required=False, label='OI Altura'
    )
    oi_adicion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OI Adición'}),
        required=False, label='OI Adición'
    )
    
    # Extras
    horizontal = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Horizontal'}),
        required=False, label='Horizontal'
    )
    vertical = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vertical'}),
        required=False, label='Vertical'
    )
    puente = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Puente'}),
        required=False, label='Puente'
    )
    distancia_mecanica = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Distancia Mecánica'}),
        required=False, label='Distancia Mecánica'
    )
    
    # Montura
    montura_descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False, label='Descripción Montura'
    )
    montura_estado = forms.ChoiceField(
        choices=EstadoMontura.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False, label='Estado Montura'
    )
    montura_foto = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False, label='Foto Montura'
    )
    
    # Bisel
    tipo_bisel = forms.ChoiceField(
        choices=TipoBisel.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False, label='Tipo de Bisel'
    )
    
    # Observaciones
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales...'
        }),
        required=False, label='Observaciones'
    )
    
    class Meta:
        model = Pedido
        fields = [
            'tipo_lente', 'diseno_lente', 'material', 'indice',
            'od_esfera', 'od_cilindro', 'od_eje', 'od_dnp', 'od_altura', 'od_adicion',
            'oi_esfera', 'oi_cilindro', 'oi_eje', 'oi_dnp', 'oi_altura', 'oi_adicion',
            'horizontal', 'vertical', 'puente', 'distancia_mecanica',
            'montura_descripcion', 'montura_estado', 'montura_foto',
            'tipo_bisel', 'observaciones',
        ]


class CampoForm(forms.ModelForm):
    """Formulario para configurar campos dinámicos."""
    tipo = forms.ChoiceField(
        choices=TipoCampo.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    categoria = forms.ChoiceField(
        choices=Campo._meta.get_field('categoria').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    requerido = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False
    )
    opciones_raw = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Una opción por línea'
        }),
        required=False,
        label='Opciones (una por línea)'
    )
    valores_temp = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'valor1, valor2'
        }),
        required=False,
        label='Mostrar cuando el valor sea',
        help_text='Valores separados por coma'
    )
    
    class Meta:
        model = Campo
        fields = [
            'nombre', 'clave', 'tipo', 'categoria',
            'requerido', 'orden', 'activo',
            'depende_de', 'opciones_raw'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'depende_de': forms.Select(attrs={'class': 'form-select'}),
            'opciones_raw': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar valores_temp con los valores actuales
        if self.instance and self.instance.valores_que_muestran:
            self.initial['valores_temp'] = ', '.join(self.instance.valores_que_muestran)
    
    def clean_opciones_raw(self):
        """Convierte las opciones de texto a lista."""
        opciones_raw = self.cleaned_data.get('opciones_raw', '')
        if opciones_raw:
            return [opt.strip() for opt in opciones_raw.split('\n') if opt.strip()]
        return []
    
    def clean_valores_temp(self):
        """Convierte valores de texto a lista."""
        valores = self.cleaned_data.get('valores_temp', '')
        if valores:
            return [v.strip() for v in valores.split(',') if v.strip()]
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Guardar opciones
        opciones_raw = self.cleaned_data.get('opciones_raw', [])
        if opciones_raw:
            instance.opciones = opciones_raw
        
        # Guardar valores de dependencia
        valores_temp = self.cleaned_data.get('valores_temp', [])
        if valores_temp:
            instance.valores_que_muestran = valores_temp
        else:
            instance.valores_que_muestran = []
        
        if commit:
            instance.save()
        return instance


class CambioEstadoForm(forms.Form):
    """Formulario para cambiar el estado de un pedido."""
    nuevo_estado = forms.ChoiceField(
        choices=EstadoPedido.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=False,
        label='Observaciones del cambio'
    )