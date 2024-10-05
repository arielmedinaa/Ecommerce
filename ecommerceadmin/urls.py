
from django.contrib import admin
from django.urls import path, include
from ecommerce import views

urlpatterns = [
    # Ruta para el registro de usuarios
    path('admin/', admin.site.urls),
    path('auth/', include('homeLogin.urls')),
    path('productos/', views.productCharge),
    path('productos/stock/', views.charge_stock),
    path('productos/<int:pk>/', views.product_detail, name='product_detail'),
    path('productos/stock/<int:pk>/', views.Stock_detail),
    path('productos/migraciones/', views.migración_producto, name='productoMigra'),
    path('ventas/', views.venta_product, name='venta_product'),
    path('ventas/<int:pk>/', views.lista_venta, name='lista_venta')
]