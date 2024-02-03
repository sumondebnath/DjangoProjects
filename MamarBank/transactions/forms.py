from typing import Any
from django import forms
from transactions.models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["account_number","amount", "transaction_type"]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop("account")        #je request korbe tar account 
        super().__init__(*args, **kwargs)       # constractor ke override korbo
        self.fields["transaction_type"].disabled = True     # transaction_type disable kore
        self.fields["transaction_type"].widget = forms.HiddenInput()        # transaction_type field tar input hidden kore dibo.

    def save(self, commit=False):
        self.instance.account = self.account        # jar account tar account khuje connect kora
        self.instance.balance_after_transaction = self.account.balance      # transaction ar por balance update kora.
        return super().save()       # save kora
    

class TransferForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    account_number = forms.IntegerField()

    
    
class DepositeForm(TransactionForm):
    def clean_amount(self):             # here Clean is a built-in keyword when we need any specific forms-fields Filter/Update kora lagle sei fields ar aga clean_ dile hobe its make built in functions. 
        min_deposit_amount = 500            # set min deposite value
        amount = self.cleaned_data.get("amount")        # user ar fill kora data theke amount data ta niye aslam
        if amount < min_deposit_amount:
            raise forms.ValidationError(                # condition full fill na hole user ke error show kora.
                f"You need to deposite at least {min_deposit_amount} BDT."
            )
        return amount                                   # condition full fill hoyai amount return kora.
    

class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdraw = 1000
        max_withdraw = 100000
        balance = account.balance
        amount = self.cleaned_data.get("amount")

        if amount < min_withdraw:
            raise forms.ValidationError(
                f"You need to withdraw at least {min_withdraw} BDT."
            )
        if amount > max_withdraw:
            raise forms.ValidationError(
                f"You need to withdraw at most {max_withdraw} BDT."
            )
        if amount > balance:
            raise forms.ValidationError(
                f"You have {balance} BDT in your account"
                "You can not withdraw more than your account balance."
            )
        
        return amount
    
class LoadRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        return amount