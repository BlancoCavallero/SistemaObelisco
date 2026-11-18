"""Serve the single-page application built by Vite."""

from pathlib import Path

from django.conf import settings
from django.http import HttpResponse

SIN_BUILD = """<!doctype html>
<html lang="es-AR"><head><meta charset="utf-8"><title>Obelisco</title></head>
<body style="font-family:system-ui;max-width:40rem;margin:4rem auto;padding:0 1rem">
<h1>El front todavia no esta construido</h1>
<p>Genera el build y volve a cargar:</p>
<pre>cd frontend &amp;&amp; npm install &amp;&amp; npm run build</pre>
</body></html>
"""


def spa(_request):
    """Return the built index.html.

    The SPA owns client-side routes, so any unknown path returns the same shell. Static
    assets are handled by WhiteNoise; API and admin routes never reach this view.
    """
    index = Path(settings.FRONTEND_DIST) / "index.html"
    if not index.exists():
        return HttpResponse(SIN_BUILD, status=503, content_type="text/html; charset=utf-8")
    return HttpResponse(index.read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
