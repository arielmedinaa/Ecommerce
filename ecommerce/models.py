from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    codigo_producto = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField()
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    control_stock = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
class Ventas(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    
# Modelo bd de las tarjetas
class Tarjetas(models.Model):
    TIPO_TRANSACCION_CHOICES = [
        (0, 'Efectivo'),
        (1, 'Tarjeta'),
    ]
    
    tipo_transaccion = models.IntegerField(choices=TIPO_TRANSACCION_CHOICES, default=0)
    pago_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.IntegerField()
    fecha_transaccion = models.DateTimeField(auto_now_add=True)