from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Payment
from transbank.webpay.webpay_plus.transaction import Transaction
import transbank.webpay.webpay_plus as webpay_plus
from .models import Producto, Inventario, Descripcion, Carrito, ItemCarrito
from django.contrib.auth.decorators import login_required

webpay_plus.commerce_code = settings.TRANSBANK_COMMERCE_CODE
webpay_plus.api_key = settings.TRANSBANK_API_KEY
webpay_plus.environment = settings.TRANSBANK_ENVIRONMENT

def prueba(request):
    return render(request, 'prueba.html')


def start_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        order_id = request.POST.get('order_id')
        session_id = request.session.session_key

        # Asegúrate de que el session_id no esté vacío
        if not session_id:
            request.session.save()
            session_id = request.session.session_key
        print(f'Session ID: {session_id}')  # Depuración

        transaction = Transaction()
        
        response = transaction.create(
            buy_order=order_id,
            session_id=session_id,
            amount=amount,
            return_url='http://127.0.0.1:8000/callback/'
        )
        print(response)  # Depuración

        # Almacenar el pago en la base de datos
        payment = Payment.objects.create(
            order_id=order_id,
            amount=amount,
            token=response['token']
        )
        
        # Redirigir a la URL proporcionada en la respuesta
        return redirect(response['url'] + '?token_ws=' + response['token'])

    return render(request, 'start_payment.html')

def payment_callback(request):
    token = request.GET.get('token_ws')
    transaction = Transaction()
    
    response = transaction.commit(token)

    if response['status'] == 'AUTHORIZED':
        payment = Payment.objects.get(token=token)
        payment.status = 'paid'
        payment.save()

    return render(request, 'payment_callback.html', {'response': response})



def product_list(request):
    productos = Producto.objects.all()
    
    product_data = []
    for producto in Producto:
        inventario = Inventario.objects.filter(CodigoProducto=producto).first()
        descripcion = Descripcion.objects.filter(CodigoProducto=producto).first()
        
        if inventario and descripcion:
            product_data.append({
                'producto': producto,
                'inventario': inventario,
                'descripcion': descripcion
            })
    
    # Imprimir datos para depuración
    if not product_data:
        print('No se encontraron productos.')
    else:
        for item in product_data:
            print(f'Producto: {item["producto"].Nombre}, Inventario: {item["inventario"].Cantidad}, Descripcion: {item["descripcion"].Detalles}')

    return render(request, 'base.html', {'product_data': product_data}) 
def product_list(request):
    productos = Producto.objects.all()  # Obtener todos los objetos del modelo Producto
    return render(request, 'product_list.html', {'productos': productos})

from django.shortcuts import render
from .models import Producto, Inventario, Descripcion

def lista_productos(request):
    productos = Producto.objects.all()
    productos_con_datos = []
    for producto in productos:
        inventario = Inventario.objects.filter(CodigoProducto=producto).first()
        descripcion = Descripcion.objects.filter(CodigoProducto=producto).first()
        productos_con_datos.append({
            'producto': producto,
            'inventario': inventario,
            'descripcion': descripcion,
        })
    return render(request, 'lista_productos.html', {'productos_con_datos': productos_con_datos})

def agregar_al_carrito(request, codigo_producto):
    producto = get_object_or_404(Producto, CodigoProducto=codigo_producto)
    inventario = get_object_or_404(Inventario, CodigoProducto=producto)
    
    if inventario.Cantidad > 0:
        carrito = request.session.get('carrito', {})

        if codigo_producto in carrito:
            carrito[codigo_producto] += 1
        else:
            carrito[codigo_producto] = 1
        
        inventario.Cantidad -= 1
        inventario.save()
        
        request.session['carrito'] = carrito

    return redirect('lista_productos')

def eliminar_del_carrito(request, codigo_producto):
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Producto, CodigoProducto=codigo_producto)
    inventario = get_object_or_404(Inventario, CodigoProducto=producto)
    
    if codigo_producto in carrito:
        if carrito[codigo_producto] > 1:
            carrito[codigo_producto] -= 1
        else:
            del carrito[codigo_producto]
        
        inventario.Cantidad += 1
        inventario.save()

        request.session['carrito'] = carrito

    return redirect('ver_carrito')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0

    for codigo_producto, cantidad in carrito.items():
        producto = get_object_or_404(Producto, CodigoProducto=codigo_producto)
        inventario = Inventario.objects.filter(CodigoProducto=producto).first()
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio': inventario.Precio,
            'total': cantidad * inventario.Precio
        })
        total += cantidad * inventario.Precio

    return render(request, 'carrito.html', {'items': items, 'total': total})