from rest_framework import serializers
from homeLogin.serializers import ProfileSerializer
from .models import Product, Ventas, Tarjetas
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'codigo_producto', 'name', 'description', 'category', 'price', 'image_url', 'stock', 'created_at', 'control_stock']
        read_only_fields = ['created_at', 'id']

    def validate_control_stock(self, value):
        if value == 0:
            return True
        return False

    def validate(self, data):
        control_stock = data.get('control_stock', None)

        # Si no se proporciona control_stock, define un valor predeterminado
        if control_stock is None:
            control_stock = True
        data['control_stock'] = self.validate_control_stock(data['stock'])

        return data
 
class StockChargeSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    
    def validate(self, data):
        id_producto = data.get('id_producto')
        cantidad = data.get('cantidad')
        #control_stock = data.get('control_stock')

        if not Product.objects.filter(id=id_producto).exists():
            raise serializers.ValidationError("El producto especificado no existe.")
        
        product = Product.objects.get(id=id_producto)

        if product.control_stock == 1:
            raise serializers.ValidationError("El producto es un servicio")
        
        if cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser un número positivo")

        return data
        
class VentasSerializer(serializers.ModelSerializer):
    usuario = ProfileSerializer(read_only=True)
    class Meta:
        model = Ventas
        fields = '__all__'
        read_only_fields = ['id', 'fecha']

    def validate(self, data):
        producto = data['producto']
        cantidad = data['cantidad']
        
        print("control_stock:", producto.control_stock)

        # Verificar si el producto requiere control de stock
        if producto.control_stock == False:
            if cantidad <= 0:
                raise serializers.ValidationError("La cantidad debe ser mayor que cero para productos que requieren control de stock")
            if producto.stock < cantidad:
                raise serializers.ValidationError("No hay suficiente stock para esta venta")

        return data

    def create(self, validated_data):
        producto = validated_data['producto']
        cantidad = validated_data['cantidad']

        if producto.control_stock == False:  # Requiere control de stock
            if cantidad <= 0:  # No puede vender con cantidad cero
                raise serializers.ValidationError("La cantidad debe ser mayor que cero para productos que requieren control de stock")
            if producto.stock < cantidad and producto.stock == 0:
                raise serializers.ValidationError("No hay suficiente stock para completar la venta")

            producto.stock -= cantidad  # Reduce el stock solo si hay suficiente
            producto.save()

        return super().create(validated_data)
    
class PagoSerializer(serializers.ModelSerializer):
    tipo_transaccion = serializers.ChoiceField(choices=Tarjetas.TIPO_TRANSACCION_CHOICES)

    class Meta:
        model = Tarjetas
        fields = ['id', 'tipo_transaccion', 'pago_usuario', 'monto', 'fecha_transaccion']
        read_only_fields = ['fecha_transaccion']
        
    def monto_precio(self, validated_data):
        producto = validated_data['producto']
        monto = producto.price
        
        validated_data['monto'] = monto
        return super().create(validated_data)