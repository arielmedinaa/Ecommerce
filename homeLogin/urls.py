from django.urls import path
from .views import login, register_user, profile, password_reset_request, password_reset_confirm

urlpatterns = [
    path('login/', login),
    path('register/', register_user),
    path('profile/', profile),
    path('password_forgot/', password_reset_request),
    path('password_reset_confirm/', password_reset_confirm),
]
