from django.urls import path
from .views import UserRegistrationView, UserAccountUpdate, UserLoginView, userLogout, ChangePassword #UserLogoutView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="log_in"),
    # path("logout/", UserLogoutView.as_view(), name='log_out'),
    path("logout/", userLogout, name="log_out"),
    path("profile/", UserAccountUpdate.as_view(), name="profile"),
    path("Change-password/", ChangePassword, name="password"),
]