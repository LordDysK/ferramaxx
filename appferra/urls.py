"""appferra URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web_ferramax import views

urlpatterns = [
    path('admin/', admin.site.urls),

    #url transbak test
    path('start_payment/', views.start_payment, name='start_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
     path('convertir_precio/', views.convertir_precio, name='convertir_precio'),
    #test
    path('products/', views.product_list, name='product_list'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('', views.lista_productos, name='lista_productos'),
    path('agregar/<str:codigo_producto>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<str:codigo_producto>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),  # Asegúrate de que esta línea esté correcta
    path('carrito/', views.ver_carrito, name='ver_carrito'),
]
