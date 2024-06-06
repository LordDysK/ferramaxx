from django.shortcuts import render, redirect
from django.conf import settings
from .models import Payment
from transbank.webpay.webpay_plus.transaction import Transaction
import transbank.webpay.webpay_plus as webpay_plus
from .models import Producto, Inventario, Descripcion

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



""" def product_list(request):
    productos = Producto.objects.all()
    
    product_data = []
    for producto in Productos:
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

    return render(request, 'base.html', {'product_data': product_data}) """
def product_list(request):
    productos = Producto.objects.all()  # Obtener todos los objetos del modelo Producto
    return render(request, 'product_list.html', {'productos': productos})