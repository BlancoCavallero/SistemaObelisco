"""Serializers for the movement ledger."""

from rest_framework import serializers

from catalogo.models import Producto

from .models import EstadoArticulo, Movimiento, Posicion


class MovimientoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            "id",
            "producto",
            "cantidad",
            "tipo",
            "estado",
            "fecha",
            "usuario",
            "motivo",
            "posicion",
            "referencia",
        ]
        read_only_fields = ["fecha", "usuario"]

    def validate_cantidad(self, value):
        if value == 0:
            raise serializers.ValidationError("La cantidad no puede ser cero.")
        return value

    def validate(self, attrs):
        # Only movements representable by a single signed quantity are accepted here.
        # `armado` and `transferencia` leave the total unchanged and are created by their
        # own endpoints, always as a pair. Accepting them one-sided here would distort
        # stock silently.
        entrada_libre = {
            "entrada_compra",
            "entrada_inventario_inicial",
            "ajuste",
        }
        tipo = attrs.get("tipo")
        if not self.instance and tipo and tipo not in entrada_libre:
            raise serializers.ValidationError(
                {"tipo": "Este tipo de movimiento se registra desde su propio circuito."}
            )
        return attrs


class _OperacionParSerializer(serializers.Serializer):
    """Base for operations that move stock between two dimensions at once."""

    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1)


class ArmarSerializer(_OperacionParSerializer):
    posicion = serializers.PrimaryKeyRelatedField(
        queryset=Posicion.objects.all(), required=False, allow_null=True
    )


class TransferirSerializer(_OperacionParSerializer):
    desde = serializers.PrimaryKeyRelatedField(queryset=Posicion.objects.all())
    hasta = serializers.PrimaryKeyRelatedField(queryset=Posicion.objects.all())
    estado = serializers.ChoiceField(choices=EstadoArticulo.choices, default="listo")

    def validate(self, attrs):
        if attrs["desde"] == attrs["hasta"]:
            raise serializers.ValidationError({"hasta": "El destino debe ser distinto del origen."})
        return attrs
