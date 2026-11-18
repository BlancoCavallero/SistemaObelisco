"""Users and versioned business parameters."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Rol(models.TextChoices):
    ADMIN = "admin", "Administracion"
    OPERADOR = "operador", "Operacion"


class Usuario(AbstractUser):
    """One user per employee. Never deleted: deactivation keeps history intact."""

    rol = models.CharField(max_length=16, choices=Rol.choices, default=Rol.OPERADOR)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.username

    def puede_administrar(self):
        return self.rol == Rol.ADMIN


class Parametro(models.Model):
    """A business parameter with an effective date.

    Rows are never updated in place: changing the margin today must not rewrite the
    margin of last month's sales. To change a value, add a new row with a later
    `vigente_desde`.
    """

    clave = models.CharField(max_length=64)
    valor = models.JSONField()
    vigente_desde = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-vigente_desde"]
        constraints = [
            models.UniqueConstraint(
                fields=["clave", "vigente_desde"], name="parametro_clave_vigencia_unica"
            )
        ]
        verbose_name = "parametro"
        verbose_name_plural = "parametros"

    def __str__(self):
        return f"{self.clave} desde {self.vigente_desde}"

    @classmethod
    def valor_vigente(cls, clave, fecha=None):
        """Return the value in effect on `fecha` (default: today), or None."""
        fecha = fecha or timezone.localdate()
        return (
            cls.objects.filter(clave=clave, vigente_desde__lte=fecha)
            .order_by("-vigente_desde")
            .values_list("valor", flat=True)
            .first()
        )
