from django.contrib import admin
from Accounts.models import UserBankAccount, UserAddress

# Register your models here.
admin.site.register(UserBankAccount)
admin.site.register(UserAddress)