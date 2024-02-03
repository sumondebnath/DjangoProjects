from django.urls import path
from transactions.views import DepositMoneyView, WithdrawMoneyView, LoanRequestView, TransactionReportView, PayLoanView, LoanListView, TransferView

urlpatterns = [
    path("deposite/", DepositMoneyView.as_view(), name="deposit_modey"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_modey"),
    path("loan-request/", LoanRequestView.as_view(), name="loan_request"),
    path("transaction-report/", TransactionReportView.as_view(), name="transaction_report"),
    path("loan-pay/<int:loan_id>/", PayLoanView.as_view(), name="pay_loan"),
    path("loan-list/", LoanListView.as_view(), name="loan_list"),
    path("money-transfer/", TransferView.as_view(), name="transfer_money"),
]