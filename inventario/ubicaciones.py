"""Warehouse layout endpoints."""

from rest_framework import serializers, viewsets

from .models import Almacen, Posicion, Sector


class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ["id", "codigo", "nombre"]


class SectorSerializer(serializers.ModelSerializer):
    almacen_codigo = serializers.ReadOnlyField(source="almacen.codigo")

    class Meta:
        model = Sector
        fields = ["id", "almacen", "almacen_codigo", "codigo"]


class PosicionSerializer(serializers.ModelSerializer):
    sector_codigo = serializers.ReadOnlyField(source="sector.codigo")
    almacen = serializers.ReadOnlyField(source="sector.almacen_id")
    etiqueta = serializers.SerializerMethodField()

    class Meta:
        model = Posicion
        fields = ["id", "sector", "sector_codigo", "almacen", "codigo", "etiqueta"]

    def get_etiqueta(self, posicion):
        return f"{posicion.sector.almacen.codigo}/{posicion.sector.codigo}/{posicion.codigo}"


class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    pagination_class = None


class SectorViewSet(viewsets.ModelViewSet):
    serializer_class = SectorSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Sector.objects.select_related("almacen")
        almacen = self.request.query_params.get("almacen")
        return queryset.filter(almacen_id=almacen) if almacen else queryset


class PosicionViewSet(viewsets.ModelViewSet):
    serializer_class = PosicionSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Posicion.objects.select_related("sector__almacen")
        almacen = self.request.query_params.get("almacen")
        sector = self.request.query_params.get("sector")
        if almacen:
            queryset = queryset.filter(sector__almacen_id=almacen)
        if sector:
            queryset = queryset.filter(sector_id=sector)
        return queryset
