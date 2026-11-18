"""Serializers for the movement ledger."""

from rest_framework import serializers

from .models import Movimiento


class MovimientoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            "id",
            "producto",
            "cantidad",
            "tipo",
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
        # Only movements that a single signed quantity can represent are accepted here.
        # `armado` (caja -> armado) and `transferencia` (position A -> position B) do not
        # change the total but do change a dimension the ledger does not have yet, so
        # accepting them would silently distort stock. They come with that dimension.
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
