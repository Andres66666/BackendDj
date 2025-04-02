# models.py
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
# models.py
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError


# Modelo de Roles
class Roles(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    estado_Rol = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_rol

# Modelo de Permisos
class Permisos(models.Model):
    nombre_permiso = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    estado_Permiso = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_permiso

# Modelo de Usuarios
class Usuarios(models.Model):
    nombre_usuario = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=50, unique=True)
    correo = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    ci = models.CharField(max_length=20, unique=True)
    ci_departamento = models.CharField(max_length=2, default='EX')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado_Usuario = models.BooleanField(default=True)

    imagen_url = models.URLField(max_length=500,null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre_usuario} {self.apellido}'

# Modelo de Roles de Usuarios
class UsuariosRoles(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')
    def __str__(self):
        return f'{self.usuario} {self.rol} '

# Modelo de Roles y Permisos
class RolesPermisos(models.Model):
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permisos, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('rol', 'permiso')
    def __str__(self):
        return f'{self.rol} {self.permiso} '
    
""" seccion de ventas para un rol especifico  """

# Modelo de Categorías
class Categorias(models.Model):
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    estado_categoria = models.BooleanField(default=True)


    def __str__(self):
        return self.nombre_categoria

# Modelo de Productos
class Productos(models.Model):
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  
    precio_mayor = models.DecimalField(max_digits=10, decimal_places=2) 
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)  
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    codigo_producto = models.CharField(max_length=50, unique=True)
    imagen_productos = models.URLField(max_length=500,null=True, blank=True)
    estado_equipo = models.BooleanField(default=True)


    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre_producto']

    def __str__(self):
        return f"{self.nombre_producto} ({self.codigo_producto})"


# Modelo de Ventas
class Ventas(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='Pendiente')  # Example: default string value
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Example: decimal default

    def __str__(self):
        return f'Venta #{self.id} realizada por {self.usuario}'

# Modelo de Detalles de Ventas
class DetallesVentas(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Example: decimal default
    tipo_venta = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        # Verificar si hay suficiente stock antes de confirmar la venta
        if self.cantidad > self.producto.stock:
            raise ValueError(f"No hay suficiente stock para {self.producto.nombre_producto}")     
        # Reducir el stock del producto
        self.producto.stock -= self.cantidad
        self.producto.save()  # Guardar el cambio en el modelo de Productos
        super().save(*args, **kwargs)  # Llamar al método save de la superclase

    def __str__(self):
        return f'Detalle de {self.cantidad} {self.producto.nombre_producto} en la venta {self.venta.id}'
