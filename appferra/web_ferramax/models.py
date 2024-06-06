from django.db import models

# Create your models here.
# payments

class Payment(models.Model):
    order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    token = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.amount}"



class Producto(models.Model):
    CodigoProducto = models.CharField(max_length=50, primary_key=True)
    Nombre = models.CharField(max_length=255)
    Marca = models.CharField(max_length=255)

    def __str__(self):
        return self.Nombre


class Inventario(models.Model):
    IdInventario = models.AutoField(primary_key=True)
    CodigoProducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    Cantidad = models.IntegerField()
    Precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.CodigoProducto} - {self.Cantidad}'

class Descripcion(models.Model):
    IdDescripcion = models.AutoField(primary_key=True)
    CodigoProducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    Detalles = models.TextField()
    Categoria = models.CharField(max_length=255)

    def __str__(self):
        return self.Categoria