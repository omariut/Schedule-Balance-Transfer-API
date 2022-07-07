from transaction.models import Account,Transfer,TransactionHistory, CashTransaction
from rest_framework.serializers import ModelSerializer,Serializer, SerializerMethodField

class AccountSerializer(ModelSerializer):
    
    class Meta:
        model =  Account
        fields = '__all__'

class TransferSerializer(ModelSerializer):
    
    class Meta:
        model =  Transfer
        fields = '__all__'


class TransactionHistorySerializer(ModelSerializer):
    
    class Meta:
        model =  TransactionHistory
        fields = '__all__'

class CashTransactionSerializer(ModelSerializer):
    
    class Meta:
        model =   CashTransaction
        fields = '__all__'


class AccountDetailSerializer(ModelSerializer):

    class Meta:
        model =  Account
        exclude = ['id','created_at', 'updated_at']
        
