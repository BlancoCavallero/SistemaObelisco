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
            "proveedor",
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
        # D-08: an adjustment without a reason is a magic number. The count screen fills
        # it in by default; a manual adjustment has to say why.
        if not self.instance and tipo == "ajuste" and not (attrs.get("motivo") or "").strip():
            raise serializers.ValidationError(
                {"motivo": "Un ajuste necesita un motivo: sin el no se puede auditar."}
            )
        return attrs


class ConteoSerializer(serializers.Serializer):
    """What the operator counted, plus the number they were looking at.

    The difference is derived on the server: asking for it would let the sign be applied
    backwards. `esperado` is the number the sheet showed, echoed back so a movement that
    happens while the operator walks the depot cannot become a phantom adjustment.
    """

    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    contado = serializers.IntegerField(min_value=0)
    esperado = serializers.IntegerField(min_value=0)
    # Solo vale para lo que sobra. Un faltante se descuenta del stock que hay: elegir una
    # pila deja la otra en negativo.
    estado = serializers.ChoiceField(
        choices=EstadoArticulo.choices, required=False, allow_blank=True
    )
    motivo = serializers.CharField(required=False, allow_blank=True)


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
