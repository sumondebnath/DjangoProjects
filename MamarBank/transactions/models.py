from django.db import models
from Accounts.models import UserBankAccount
from transactions.constants import TRANSACTION_TYPE

# Create your models here.
class Bankrupt(models.Model):
    is_bankrupt = models.BooleanField(default=False, blank=True, null=True)




class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name="transactions", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)
    account_number = models.IntegerField(blank=True, null=True)
    # is_bankrupt = models.ForeignKey(Bankrupt, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["timestamp"]        # ordering is a built-in function, used for sorting.