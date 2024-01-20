from django.shortcuts import render, redirect
from django.views.generic import FormView
from Accounts.forms import UserRegistrationForm, UpdateUserForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View

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

class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy("home")
    
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