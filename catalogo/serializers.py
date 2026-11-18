"""Serializers for the product catalog."""

from rest_framework import serializers

from .models import Categoria, Producto, TipoProducto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "activo"]


class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        fields = ["id", "categoria", "nombre"]


class ProductoSerializer(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField()
    id_visible = serializers.ReadOnlyField()
    precio_venta = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id",
            "tipo",
            "color",
            "alto_cm",
            "ancho_cm",
            "largo_cm",
            "modelo",
            "nombre",
            "id_visible",
            "precio_venta",
            "stock",
            "activo",
        ]
        read_only_fields = ["activo"]
        # The generated unique-together validator would answer 400 and lose the useful
        # detail. `buscar_duplicado` answers 409 with the existing product instead, so
        # the operator can add stock to it. The database constraint still guards.
        validators = []

    def get_stock(self, producto):
        from inventario.stock import stock_de

        return stock_de(producto)

    def get_precio_venta(self, producto):
        precio = producto.precio_venta()
        # Decimal("11000").quantize(Decimal("1E2")) prints as "1.1E+4": format it fixed.
        return None if precio is None else f"{precio:.2f}"

    def buscar_duplicado(self):
        """Return the existing product with the same attributes, if any.

        This is the guard that stops the same article from being created twice and
        splitting its stock in two.
        """
        data = self.validated_data
        required = ("tipo", "color", "alto_cm", "ancho_cm", "largo_cm")
        if not all(field in data for field in required):
            return None
        return Producto.objects.filter(
            tipo=data["tipo"],
            color=data["color"],
            alto_cm=data["alto_cm"],
            ancho_cm=data["ancho_cm"],
            largo_cm=data["largo_cm"],
            modelo=(data.get("modelo") or "").strip(),
        ).first()
