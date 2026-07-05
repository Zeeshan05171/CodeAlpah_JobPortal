from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, MeView,
    EmployerProfileUpdateView, CandidateProfileUpdateView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/employer/", EmployerProfileUpdateView.as_view(), name="employer-profile"),
    path("profile/candidate/", CandidateProfileUpdateView.as_view(), name="candidate-profile"),
]
