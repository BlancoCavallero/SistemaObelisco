"""Staff session routes."""

from django.urls import path

from .auth import LoginView, LogoutView, PerfilView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", PerfilView.as_view(), name="perfil"),
]
