"""Serializers for the supplier directory."""

from rest_framework import serializers

from .models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            "id",
            "nombre",
            "canal",
            "contacto",
            "telefono",
            "email",
            "notas",
            "activo",
        ]
