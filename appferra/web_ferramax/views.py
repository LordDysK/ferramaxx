from django.shortcuts import render, redirect
from django.conf import settings
from .models import Payment
from transbank.webpay.webpay_plus.transaction import Transaction



def prueba(request):
    return render(request, 'prueba.html')

def start_payment(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        order_id = request.POST['order_id']

        transaction = Transaction(webpay_plus_default_commerce_code='your_commerce_code',
                                  webpay_plus_default_api_key=settings.TRANSBANK_API_KEY)
        
        response = transaction.create(order_id, session_id, amount, return_url='http://yourdomain/payments/callback/')

        if response['status'] == 'INITIALIZED':
            payment = Payment.objects.create(
                order_id=order_id,
                amount=amount,
                token=response['token']
            )
            return redirect(response['url'] + '?token_ws=' + response['token'])

    return render(request, 'start_payment.html')

def payment_callback(request):
    token = request.GET.get('token_ws')
    transaction = Transaction(webpay_plus_default_commerce_code='your_commerce_code',
                              webpay_plus_default_api_key=settings.TRANSBANK_API_KEY)
    
    response = transaction.commit(token)

    if response['status'] == 'AUTHORIZED':
        payment = Payment.objects.get(token=token)
        payment.status = 'paid'
        payment.save()

    return render(request, 'payment_callback.html', {'response': response})

# Create your views here.
