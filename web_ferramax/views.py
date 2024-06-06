from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Payment
from transbank.webpay.webpay_plus.transaction import Transaction
import transbank.webpay.webpay_plus as webpay_plus
from .models import Producto, Inventario, Descripcion, Carrito, ItemCarrito, models
from django.http import HttpResponse
import uuid
import requests
from django.http import JsonResponse, HttpResponse
from django.contrib import messages

webpay_plus.commerce_code = settings.TRANSBANK_COMMERCE_CODE
webpay_plus.api_key = settings.TRANSBANK_API_KEY
webpay_plus.environment = settings.TRANSBANK_ENVIRONMENT

def prueba(request):
    return render(request, 'prueba.html')

def obtener_tasa_de_cambio():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        tasa_cambio = data['rates']['CLP']
        return tasa_cambio
    except Exception as e:
        print(f"Error al obtener la tasa de cambio: {e}")
        return None

def start_payment(request):
    if request.method == 'POST':
        amount_clp = request.POST.get('amount_clp')
        print(f'Amount CLP: {amount_clp}')  # Depuración

        # Generar un ID de pedido único corto
        order_id = str(uuid.uuid4())[:26]
        session_id = request.session.session_key

        # Asegúrate de que el session_id no esté vacío
        if not session_id:
            request.session.save()
            session_id = request.session.session_key
        print(f'Session ID: {session_id}')  # Depuración

        transaction = Transaction()
        
        try:
            response = transaction.create(
                buy_order=order_id,
                session_id=session_id,
                amount=amount_clp,
                return_url='http://127.0.0.1:8000/callback/'
            )
            print(response)  # Depuración

            # Almacenar el pago en la base de datos
            payment = Payment.objects.create(
                order_id=order_id,
                amount=amount_clp,
                token=response['token']
            )
            
            # Redirigir a la URL proporcionada en la respuesta
            return redirect(response['url'] + '?token_ws=' + response['token'])
        except Exception as e:
            return HttpResponse(f"Error al iniciar el pago: {e}", status=400)

    return render(request, 'start_payment.html')



def payment_callback(request):
    token = request.GET.get('token_ws')
    transaction = Transaction()
    
    response = transaction.commit(token)

    if response['status'] == 'AUTHORIZED':
        payment = Payment.objects.get(token=token)
        payment.status = 'paid'
        payment.save()

        # Eliminar objetos del carrito
        carrito = request.session.get('carrito', {})
        for codigo_producto, cantidad in carrito.items():
            eliminar_del_carrito(request, codigo_producto)

        messages.success(request, "¡Pago autorizado! Los productos del carrito han sido eliminados.")
    elif response['status'] == 'REJECTED':
        messages.error(request, "¡Pago rechazado! Por favor, inténtelo nuevamente o contacte al soporte.")
    else:
        messages.error(request, "El pago no fue autorizado.")

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

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))

        if inventario.Cantidad >= cantidad:
            carrito = request.session.get('carrito', {})

            if codigo_producto in carrito:
                carrito[codigo_producto] += cantidad
            else:
                carrito[codigo_producto] = cantidad
            
            inventario.Cantidad -= cantidad
            inventario.save()
            
            request.session['carrito'] = carrito
        else:
            return HttpResponse("No hay suficiente cantidad en inventario", status=400)

    return redirect('lista_productos')

def eliminar_del_carrito(request, codigo_producto):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = request.session.get('carrito', {})
        producto = get_object_or_404(Producto, CodigoProducto=codigo_producto)
        inventario = get_object_or_404(Inventario, CodigoProducto=producto)
        
        if codigo_producto in carrito:
            if carrito[codigo_producto] > cantidad:
                carrito[codigo_producto] -= cantidad
            else:
                cantidad = carrito[codigo_producto]
                del carrito[codigo_producto]
            
            inventario.Cantidad += cantidad
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
        subtotal = cantidad * inventario.Precio
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio': inventario.Precio,
            'total': subtotal
        })
        total += subtotal

    return render(request, 'carrito.html', {'items': items, 'total': total})

def convertir_precio(request):
    if request.method == 'GET':
        total_dolares = request.GET.get('total', None)
        if total_dolares is not None:
            try:
                total_dolares = float(total_dolares)
                tasa_cambio = obtener_tasa_de_cambio()
                if tasa_cambio:
                    total_pesos = total_dolares * tasa_cambio
                    total_pesos_redondeado = round(total_pesos)
                    return JsonResponse({'total_pesos': total_pesos_redondeado, 'tasa_cambio': tasa_cambio})
                else:
                    return JsonResponse({'error': 'Error al obtener la tasa de cambio'}, status=500)
            except ValueError:
                return JsonResponse({'error': 'Total inválido'}, status=400)
        else:
            return JsonResponse({'error': 'Falta el parámetro total'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)