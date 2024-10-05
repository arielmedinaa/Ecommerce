import os
import pandas as pd
import openpyxl
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from .serializers import ProductSerializer, VentasSerializer, StockChargeSerializer, PagoSerializer
from .process import MigracionProducto
from .models import Product, Ventas
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

#Haciendo carga de productos
#Haciendo consulta de todos los productos existentes
@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def productCharge(request):
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():            
            # Verificar si ya existe un producto con el mismo código
            codigo_producto = serializer.validated_data['codigo_producto']
            existing_product = Product.objects.filter(codigo_producto=codigo_producto).first()
            if existing_product:
                return Response({'Error': 'El producto ya existe'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        # Obtener todos los productos
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

#Carga manual de stock (simulacro de entrada de stock)
@api_view(['POST'])
def charge_stock(request):
    serializer = StockChargeSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            validated_data = serializer.validated_data
            product_id = validated_data['id_producto']
            quantity = validated_data['cantidad']

            product = Product.objects.get(id=product_id)
            product.stock += quantity
            product.save()

            return Response({'message': 'Carga de stock exitosa'}, status=status.HTTP_201_CREATED)
        
        except serializer.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Consulta específica del stock (por si se quiera detallar esa información)
@api_view(['GET'])
def Stock_detail(request, pk):
    if request.method == 'GET':
        try:
            # Encuentra el producto por su ID
            product = Product.objects.get(pk=pk)
            response_data = {
                'id': product.id,
                'codigo_producto': product.codigo_producto,
                'name': product.name,
                'stock': product.stock
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
                return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

#Consulta de los productos (por id y por todos los productos creados)
@api_view(['GET', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'El producto no existe'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        product.delete()
        return Response({'Producto eliminado con satisfacción'}, status=status.HTTP_204_NO_CONTENT)

#Migración de productos por medio de Excel, guardandolo en la bd
@api_view(["POST"])
#@permission_classes([IsAdminUser])
def migración_producto(request):
    form = MigracionProducto(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES["file"]
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file, engine='openpyxl')
            for _, row in df.iterrows():
                Product.objects.update_or_create(
                    codigo_producto=row['codigo_producto'],
                    defaults={
                        'name': row['name'],
                        'description': row['description'],
                        'category': row['category'],
                        'price': row['price'],
                        'image_url': row['image_url'],
                        'stock': row['stock'],
                        'control_stock': row['control_stock']
                    }
                )
            return Response("Productos importados exitosamente.", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(f"Error al importar productos: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
    return Response("El formulario no es correcto", status=status.HTTP_400_BAD_REQUEST)

#Post y Get de ventas, principalmente disminuyendo el stock (es la principal función hasta el momento...)
@api_view(['POST', 'GET']) 
def venta_product(request):
    if request.method == 'POST':
        venta_serializer = VentasSerializer(data=request.data)
        if venta_serializer.is_valid():
            venta = venta_serializer.save()
            
            # Obtener el precio del producto vendido
            monto = venta.producto.price
            pago_data = {
                'tipo_transaccion': request.data.get('tipo_transaccion'),
                'monto': monto,
                'pago_usuario': request.user.pk,
            }
            pago_serializer = PagoSerializer(data=pago_data)
            if pago_serializer.is_valid():
                pago = pago_serializer.save()
                venta.pago = pago
                venta.save()
                return Response({'message': 'Venta realizada con éxito'}, status=status.HTTP_201_CREATED)
            else:
                # Si el pago no es válido, eliminar la venta creada
                venta.delete()
                return Response(pago_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(venta_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        ventas_lista = Ventas.objects.all()
        serializer = VentasSerializer(ventas_lista, many=True)
        return Response(serializer.data)

#Apartado de consulta de los productos vendidos por id (únicamente por id)
@api_view(['GET'])
def lista_venta(request, pk):
    try:
        venta = Ventas.objects.get(pk=pk)
    except Ventas.DoesNotExist:
        return Response({'No se tiene registrado una venta'}, status=status.HTTP_400_BAD_REQUEST)
    #---consulta de las ventas por id de venta---
    if request.method == 'GET':
        serializer = VentasSerializer(venta)
        return Response(serializer.data)
    