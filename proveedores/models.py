"""Supplier directory.

The business buys by WhatsApp, phone, email, a travelling rep or a factory portal, and
does not issue purchase orders (S57). So the useful information is who they are and how
they are reached, not an approval workflow.
"""

from django.db import models


class CanalContacto(models.TextChoices):
    WHATSAPP = "whatsapp", "WhatsApp"
    TELEFONO = "telefono", "Telefono"
    EMAIL = "email", "Email"
    VIAJANTE = "viajante", "Viajante"
    PORTAL = "portal", "Portal web de la fabrica"


class Proveedor(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    canal = models.CharField(
        max_length=16, choices=CanalContacto.choices, default=CanalContacto.WHATSAPP
    )
    contacto = models.CharField(max_length=120, blank=True, default="")
    telefono = models.CharField(max_length=40, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    notas = models.CharField(max_length=200, blank=True, default="")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre
