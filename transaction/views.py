from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView, ListAPIView, get_object_or_404, RetrieveAPIView
from transaction.serializers import AccountSerializer,TransferSerializer,TransactionHistorySerializer,  CashTransactionSerializer,AccountDetailSerializer
from transaction.models import Account, Transfer,  CashTransaction, TransactionHistory
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.utils.decorators import method_decorator
from transaction.tasks.transfer import schedule_transfer
from datetime import datetime, timedelta, date
from django.db import transaction
from django.utils import timezone
from utils.validators import validate_positive_amount, check_transfer_not_in_same_account,check_account_exist_in_db
from django.core.exceptions import BadRequest
from django.http import HttpResponse

# Create your views here.


class AccountListCreateAPIView(ListCreateAPIView):
    serializer_class = AccountSerializer
    queryset = Account.objects.filter()
    def create(self, request, *args, **kwargs):
        data = request.data
        validate_positive_amount(data,data['balance'])
        return super().create(request, *args, **kwargs)

class AccountRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = AccountDetailSerializer
    queryset = Account.objects.filter()
    lookup_field = 'id'
    http_method_names = ['get','patch']

    def patch(self, request, *args, **kwargs):
        if request.data.get('balance'):
            value = request.data['balance']
            validate_positive_amount(request.data, value)
        return super().patch(request, *args, **kwargs)


class TransferListCreateAPIView(ListCreateAPIView):
    serializer_class = TransferSerializer
    queryset = Transfer.objects.filter().select_related('source_account', 'destination_account')


    def create(self, request):
        for data in request.data:
            validate_positive_amount(data,  data['amount'])
            check_transfer_not_in_same_account(data)
            

        with transaction.atomic():
            #must maintain the order
            self.bulk_update_accounts(request, 'source_account')
            self.bulk_update_accounts(request, 'destination_account')
            data = self.bulk_create_transfers(request)
        serializer = self.serializer_class(data, many = True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def bulk_create_transfers(self,request):
        transfers = request.data
        transfer_objects_to_create = (
            Transfer(source_account_id=transfer['source_account'], 
            destination_account_id=transfer['destination_account'], 
            amount=transfer['amount'],
            time = transfer.get('time', timezone.now()),
            status='success') for transfer in transfers
        )
        return Transfer.objects.bulk_create(transfer_objects_to_create) 
    
    def get_adjusted_account_balance_after_transfer_with_creating_transaction_history(self, accounts, transfers, account_type):
        transaction_history_objects = []
        mapping_source_account_balances = {}
        for account in accounts:
            id = account['id']
            balance = account['balance']
            mapping_source_account_balances[id] = balance

        for transfer_data in transfers:
            current_time = timezone.now()
            if  transfer_data.get('time',None):
                transfer_time = datetime.fromisoformat( transfer_data.get('time'))
                
            else:
                transfer_time = current_time
            amount = transfer_data['amount']
            id = transfer_data[account_type]
            
            if account_type == 'source_account':
                source_account_old_balance = mapping_source_account_balances[id]
                transaction_history = TransactionHistory(account_id = id, transfer_account_id=transfer_data['destination_account'], amount= amount, old_balance = source_account_old_balance, type ='debit', )
                mapping_source_account_balances[id] = mapping_source_account_balances[id] - amount
                if mapping_source_account_balances[id] < 0:
                    error_message = {"message": "Balance Shortage", "data": transfer_data}
                    raise BadRequest(error_message)
                
                if transfer_time > current_time:
                    #schedule_transfer(transfer_data, source_account_old_balance)
                    schedule_transfer.apply_async(args=[transfer_data,source_account_old_balance], eta= transfer_data['time'] )
                    self.request.data.remove(transfer_data)
                    continue
                

            else:
                if transfer_time <= current_time:
                    transaction_history = TransactionHistory(account_id = id, transfer_account_id=transfer_data['source_account'], amount= amount, old_balance = mapping_source_account_balances[id], type ='credit', )
                    mapping_source_account_balances[id] =  mapping_source_account_balances[id] + amount
                else:
                    continue
            
            transaction_history.new_balance = mapping_source_account_balances[id]
            transaction_history_objects.append(transaction_history)

        TransactionHistory.objects.bulk_create(transaction_history_objects)
        adjusted_account_balance = mapping_source_account_balances
        return adjusted_account_balance

    def bulk_update_accounts(self,request,account_type:str):  
        account_ids = [item['source_account']  if account_type == 'source_account' else item['destination_account'] for item in request.data ]
        accounts_from_db = Account.objects.filter(id__in = account_ids).values('id', 'balance')
        account_ids_in_db = {}
        for item in accounts_from_db:
            account_ids_in_db[item['id']] = item['id']
        check_account_exist_in_db(account_ids, account_ids_in_db)
        transfers = request.data
        adjusted_account_balance = self.get_adjusted_account_balance_after_transfer_with_creating_transaction_history(accounts_from_db, transfers, account_type)
        
        account_objects_to_update = [Account(id = key, balance=value) for key,value in adjusted_account_balance.items()]
        Account.objects.bulk_update(account_objects_to_update, ['balance'])

class TransferListAPIView(ListAPIView):
    serializer_class = TransferSerializer
    queryset = Transfer.objects.filter().select_related('source_account', 'destination_account')

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')
        get_object_or_404(Account, id = account_id )
        return Transfer.objects.filter(source_account =account_id)
    

class  CashTransactionListCreateAPIView(ListCreateAPIView):
    serializer_class =  CashTransactionSerializer
    queryset =  CashTransaction.objects.filter()

 
    def create(self, request, *args, **kwargs):
        dw_obj = [ CashTransaction(account_id=data['account'], type=data['type'], amount = data['amount'], status='success') for data in request.data]
        account_ids = [item['account'] for item in request.data]
        accounts = Account.objects.filter(id__in = account_ids).values('id', 'balance')
        account_ids_in_db = {}
        for item in accounts:
            account_ids_in_db[item['id']] = item['id']

        check_account_exist_in_db(account_ids, account_ids_in_db)
        history_objects = []
        mapping_account_balances = {}
        
        for account in accounts:
            account_id, balance = account['id'], account['balance'] 
            mapping_account_balances[account_id] = balance
        
        for data in request.data:
            account = data['account']
            amount = data['amount']
            old_balance = mapping_account_balances[account]
            type = data['type']
            
            if type == 'deposit':
                new_balance = old_balance + amount
            
            elif type =='withdrawal':
                new_balance = old_balance - amount
            else:
                error_message = {"message": "Unknown type", "data": type}
                raise ValueError(error_message)

            mapping_account_balances[account] = new_balance
    
            if mapping_account_balances[account] < 0:
                error_message = {"message": "Balance Shortage", "data": data}
                raise ValueError(error_message)
        
            his_obj = TransactionHistory(account_id=account, type=type, old_balance=old_balance,amount=amount,new_balance=new_balance)
            history_objects.append(his_obj)
        
        account_objs = []
        
        for key,value in mapping_account_balances.items():
            obj = Account(id = key, balance= value)
            account_objs.append(obj)

        with transaction.atomic():
            data =  CashTransaction.objects.bulk_create(dw_obj)
            Account.objects.bulk_update(account_objs, fields = ['balance'])
            TransactionHistory.objects.bulk_create(history_objects)
        
        serializer = self.serializer_class(data,many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class  CashTransactionListAPIView(ListAPIView):
    serializer_class =  CashTransactionSerializer
    queryset =  CashTransaction.objects.filter()

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')
        get_object_or_404(Account, id = account_id )
        return  CashTransaction.objects.filter(account=account_id)


class TransactionHistoryListAPIView(ListAPIView):
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.filter().select_related('transfer_account').values('id','account','old_balance','new_balance', 'amount', 'type').order_by('created_at')

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')
        get_object_or_404(Account, id = account_id )
        return TransactionHistory.objects.filter(account=account_id)

def reset_db(request):
    Transfer.objects.all().delete()
    TransactionHistory.objects.all().delete()
    CashTransaction.objects.all().delete()
    Account.objects.all().update(balance=500)
    data =  Account.objects.all()
    
    return HttpResponse(content=data)


