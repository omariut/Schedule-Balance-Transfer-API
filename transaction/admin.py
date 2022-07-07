from django.contrib import admin
from transaction.models import Account, Transfer,TransactionHistory, CashTransaction
# Register your models here.
admin.site.register(Account)
admin.site.register(Transfer)
admin.site.register(TransactionHistory)
admin.site.register( CashTransaction)