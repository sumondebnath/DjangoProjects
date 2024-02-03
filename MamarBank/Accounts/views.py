from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import FormView
from Accounts.forms import UserRegistrationForm, UpdateUserForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from transactions.views import send_transaction_mail

# Create your views here.
class UserRegistrationView(FormView):
    template_name = "Accounts/userRegistration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        print(form.cleaned_data)
        print(user)
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = "Accounts/userLogin.html"
    def get_success_url(self):
        return reverse_lazy("home")


# class UserLogoutView(LogoutView):
#     def get_success_url(self):
#         if self.request.user.is_authenticated:
#             logout(self.request)
#         return reverse_lazy("log_in")
    
def userLogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("log_in")
    
class UserAccountUpdate(View):
    template_name = "Accounts/profile.html"

    def get(self, request):
        form = UpdateUserForm(instance=request.user)
        return render(request, self.template_name, {"form":form})
    
    def post(self, request):
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")
        return render(request, self.template_name, {"form":form})
    
def ChangePassword(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = SetPasswordForm(user=request.user, data = request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, "Your Password Changed Successfully.")
                send_transaction_mail(request.user, None, "Password Change", "Accounts/password_mail.html")
                return redirect("home")
        else:
            form = SetPasswordForm(user=request.user)
        return render(request, "Accounts/password.html", {"form":form})
    else:
        return redirect("log_in")