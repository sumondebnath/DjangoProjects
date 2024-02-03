from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from transactions.models import Transaction, Bankrupt
from transactions.forms import DepositeForm, WithdrawForm, LoadRequestForm, TransferForm
from transactions.constants import DEPOSITE, WITHDRAW, LOAN, LOAN_PAID, TRANSFER, RECEIVE
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from Accounts.models import UserBankAccount

# Create your views here.

def send_transaction_mail(user, amount, subject, template):
        message = render_to_string(template, {
            "user" : user,
            "amount" : amount,
        })
        # to_mail = user.email
        send_mail = EmailMultiAlternatives(subject, "", to=[user.email])
        send_mail.attach_alternative(message, "text/html")
        send_mail.send()

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = "transactions/transaction_form.html"
    title = ""
    success_url = reverse_lazy("transaction_report")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "account":self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title" : self.title,
        })
        return context

class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositeForm
    title = "Deposite"
    success_url = reverse_lazy("transaction_report")

    def get_initial(self):
        initial = {"transaction_type" : DEPOSITE}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        account.balance += amount

        account.save(
            update_fields = ["balance"]
        )
        messages.success(self.request, f"{amount} BDT was deposited to your account successfully.")

        # mail_subject = "Deposite Message!"
        # message = render_to_string("transactions/deposite_mail.html", {
        #     "user" : self.request.user,
        #     "amount" : amount,
        # })
        # to_mail = self.request.user.email
        # # send_mail = EmailMessage(mail_subject, message, to=[to_mail])
        # send_mail = EmailMultiAlternatives(mail_subject, "", to=[to_mail])
        # send_mail.attach_alternative(message, "text/html")
        # send_mail.send()

        send_transaction_mail(self.request.user, amount, "Deposite Message", "transactions/deposite_mail.html")
        return super().form_valid(form)
    
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = "Withdraw"

    def get_initial(self):
        initial = {"transaction_type" : WITHDRAW}
        return initial
    
    def form_valid(self, form):
        if Bankrupt.is_bankrupt == True:
            messages.warning(self.request, "The Bank is Bankrupt! You can not Withdraw your Deposited ammount.")
        else:
            amount = form.cleaned_data.get("amount")
            account = self.request.user.account
            account.balance -= amount

            account.save(
                update_fields = ["balance"]
            )
            messages.success(self.request, f"Successfully withdrawn {amount} BDT from your account.")

            send_transaction_mail(self.request.user, amount, "Withdrawal Message", "transactions/withdrawal_mail.html")
        return super().form_valid(form)
    

class LoanRequestView(TransactionCreateMixin):
    form_class = LoadRequestForm
    title = "Request For Loan"

    def get_initial(self):
        initial = {"transaction_type" : LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type=LOAN, loan_approve=True).count()

        if current_loan_count >= 3:
            return HttpResponse("You have crossed your limits.")
        messages.success(self.request, f"Loan request for {amount} BDT approval is pending.")

        send_transaction_mail(self.request.user, amount, "Loan Request Message", "transactions/loan_request_mail.html")
        return super().form_valid(form)
    

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transactions/transaction_report.html"
    model = Transaction
    balance = 0
    context_object_name = "report_list"

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.account
        )
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(timestamp__date__gte = start_date, timestamp__date__lte=end_date)

            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum("amount"))["amount__sum"]
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "account" : self.request.user.account
        })
        return context
    

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect("loan_list")
            else:
                messages.error(self.request, f"Loan amount is greater than available balance.")
                return redirect("loan_list")
            


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/loan_request.html"
    context_object_name = "loans"

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type=LOAN)
        return queryset
    
class TransferView(LoginRequiredMixin, View):
    template_name = "transactions/transfer_money.html"

    def get(self, request):
        form = TransferForm()
        return render(request, self.template_name, {"form":form, "title":"Transfer Money"})
    
    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            account = form.cleaned_data["account_number"]
            # print(amount)
            # print(account)
            current_user = self.request.user.account
            try:
                sending_user = UserBankAccount.objects.get(account_number = account)
                # print(sending_user)
                if current_user.balance > amount:
                    current_user.balance -= amount
                    current_user.save()
                    sending_user.balance += amount
                    sending_user.save()
                    messages.success(request, "Successfully Transfered money.")
                    Transaction.objects.create(
                        account = current_user,
                        amount = amount,
                        balance_after_transaction = current_user.balance,
                        transaction_type = TRANSFER
                    )
                    Transaction.objects.create(
                        account = sending_user,
                        amount = amount,
                        balance_after_transaction = sending_user.balance,
                        transaction_type = RECEIVE
                    )
                    send_transaction_mail(self.request.user, amount, "Money Transfer", "transactions/sender_mail.html")
                    send_transaction_mail(sending_user.user, amount, "Money Received", "transactions/receiver_mail.html")

                else:
                    messages.error(request, "Not enough money in your account.")
                
            except UserBankAccount.DoesNotExist:
                messages.error(request, "Not a valid Account Number, Please check the Number and Try again.")
            
            return render(request, self.template_name, {"form":form, "title":"Transfer Money"})