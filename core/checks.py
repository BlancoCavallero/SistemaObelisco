"""Guardas de configuracion que corren al arrancar.

La peor falla de deploy no es la que rompe: es la que arranca igual y queda insegura.
Un SECRET_KEY de desarrollo en produccion firma sesiones con un valor publico.
"""

from django.conf import settings
from django.core.checks import Error, register

CLAVE_DE_DESARROLLO = "dev-insecure-key-change-me"


@register()
def secret_key_de_produccion(app_configs, **kwargs):
    problemas = []
    if not settings.DEBUG and settings.SECRET_KEY == CLAVE_DE_DESARROLLO:
        problemas.append(
            Error(
                "SECRET_KEY sigue siendo la de desarrollo con DEBUG apagado.",
                hint=(
                    "Configura la variable SECRET_KEY en el entorno. Ojo: el secret de "
                    "GitHub se llama DJANGO_SECRET_KEY, pero la variable que lee la app "
                    "es SECRET_KEY."
                ),
                id="core.E001",
            )
        )
    return problemas
