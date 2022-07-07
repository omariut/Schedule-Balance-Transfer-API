from django.urls import path
from transaction.views import AccountListCreateAPIView, CashTransactionListAPIView, TransferListAPIView, AccountRetrieveUpdateAPIView, CashTransactionListCreateAPIView, TransferListCreateAPIView, TransactionHistoryListAPIView, reset_db

urlpatterns = [
    path('accounts', AccountListCreateAPIView.as_view(), name='list_create_accounts'),
    path('accounts/<int:id>', AccountRetrieveUpdateAPIView.as_view(), name='get_update_account'),
    path('cash_transactions', CashTransactionListCreateAPIView.as_view(), name='list_create_cash_transactions'),
    path('cash_transactions/<int:account_id>', CashTransactionListAPIView.as_view(), name='get_update_cash_transactions'),
    path('transfers', TransferListCreateAPIView.as_view(), name='list_create_transfers'),
    path('transfers/<int:account_id>', TransferListAPIView.as_view(), name='list_transfers_by_account'),
    path('histories/<int:account_id>', TransactionHistoryListAPIView.as_view(), name='list_histories_by_account'),
    path('reset_db', reset_db, name = 'reset_db')

]
