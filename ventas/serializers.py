"""Serializers for sales. Prices are computed here, never accepted from the client."""

from decimal import Decimal

from rest_framework import serializers

from catalogo.models import Producto

from .models import Cliente, LineaVenta, Venta


def _dinero(valor):
    """Two decimals, never scientific notation: Decimal("1.1E+4") is 11000."""
    return None if valor is None else f"{Decimal(valor):.2f}"


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            "id",
            "nombre",
            "ciudad",
            "direccion",
            "telefono",
            "habilitado_cuenta_corriente",
            "activo",
        ]


class LineaEntradaSerializer(serializers.Serializer):
    """Only product and quantity. Any price sent by the client is ignored on purpose."""

    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1)


class VentaSerializer(serializers.ModelSerializer):
    lineas = LineaEntradaSerializer(many=True, write_only=True)
    detalle = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Venta
        fields = [
            "id",
            "fecha",
            "usuario",
            "cliente",
            "medio_pago",
            "descuento_porcentaje",
            "total",
            "confirmada",
            "lineas",
            "detalle",
        ]
        read_only_fields = ["fecha", "usuario", "descuento_porcentaje", "total", "confirmada"]

    def get_detalle(self, venta):
        return [
            {
                "producto": linea.producto_id,
                "nombre": linea.producto.nombre,
                "cantidad": linea.cantidad,
                "precio_unitario": _dinero(linea.precio_unitario),
                "subtotal": _dinero(linea.subtotal()),
            }
            for linea in venta.lineas.select_related("producto")
        ]

    def validate_lineas(self, lineas):
        if not lineas:
            raise serializers.ValidationError("Una venta necesita al menos una linea.")

        faltantes = [
            linea["producto"].nombre for linea in lineas if linea["producto"].precio_venta() is None
        ]
        if faltantes:
            raise serializers.ValidationError(
                "Falta el precio de lista de: " + ", ".join(faltantes)
            )
        return lineas

    def create(self, validated_data):
        from .services import confirmar_venta

        lineas = validated_data.pop("lineas")
        usuario = self.context["request"].user

        venta = Venta.objects.create(usuario=usuario, **validated_data)
        for linea in lineas:
            LineaVenta.objects.create(
                venta=venta,
                producto=linea["producto"],
                cantidad=linea["cantidad"],
                precio_unitario=linea["producto"].precio_venta(),
            )

        try:
            confirmar_venta(venta)
        except ValueError as error:
            raise serializers.ValidationError({"detail": str(error)}) from error

        return venta
