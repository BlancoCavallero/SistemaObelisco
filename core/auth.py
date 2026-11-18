"""Session login for the staff app.

Sessions last 90 days on purpose (design D-03): a login prompt between two sales makes
people share one account, and then no movement has a real author.
"""

from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


def _perfil(usuario):
    return {
        "id": usuario.pk,
        "username": usuario.username,
        "nombre": usuario.get_full_name() or usuario.username,
        "rol": usuario.rol,
    }


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""

        if not username or not password:
            return Response(
                {"detail": "Usuario y contrasena son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ModelBackend already rejects inactive users (user_can_authenticate), so a
        # deactivated account and a wrong password are indistinguishable here. That is
        # deliberate: answering "your account is disabled" would let anyone enumerate
        # valid usernames. The admin sees the real state in the user list.
        usuario = authenticate(request, username=username, password=password)
        if usuario is None:
            return Response(
                {"detail": "Usuario o contrasena incorrectos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, usuario)
        return Response(_perfil(usuario))


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(APIView):
    def get(self, request):
        return Response(_perfil(request.user))
