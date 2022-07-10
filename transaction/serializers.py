from transaction.models import Account, Transfer, TransactionHistory, CashTransaction
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    CharField,
    DateTimeField
)


class BaseSerializer(ModelSerializer):
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)
class AccountSerializer(BaseSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class TransferSerializer(BaseSerializer):
    status = CharField(read_only=True)

    class Meta:
        model = Transfer
        fields = "__all__"


class TransactionHistorySerializer(BaseSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class CashTransactionSerializer(BaseSerializer):
    class Meta:
        model = CashTransaction
        fields = "__all__"


class AccountDetailSerializer(ModelSerializer):
    class Meta:
        model = Account
        exclude = ["id", "created_at", "updated_at"]
