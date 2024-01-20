from django.urls import path
from Accounts.views import UserRegistrationView, UserLoginView, UserLogoutView, UserAccountUpdate

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", UserAccountUpdate.as_view(), name="profile"),
]