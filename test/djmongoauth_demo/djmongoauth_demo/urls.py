from django.urls import path

from demo.views import register, login, logout, verify_email, reset_password

urlpatterns = [
    path(
        route="register",
        view=register
    ),
    path(
        route="login",
        view=login
    ),
    path(
        route="logout",
        view=logout
    ),
    path(
        route="verify",
        view=verify_email
    ),
    path(
        route="reset",
        view=reset_password
    )
]
