from django.db import models
from datetime import datetime
from utils.validators import validate_positive_amount

# Create your models here.


class StatusType(models.TextChoices):
    SUCCESS = "success", ("success")
    PENDING = "pending", ("pending")
    ABORTED = "aborted", ("aborted")


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Account(BaseModel):
    name = models.CharField(max_length=150)
    contact = models.CharField(
        max_length=150,
        unique=True,
    )
    balance = models.FloatField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "accounts"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["balance"]),
        ]

    def __str__(self):
        return str(self.name)


class CashTransaction(BaseModel):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", ("deposit")
        WITHDRAWAL = "withdrawal", ("withdrawal")

    account = models.ForeignKey("Account", on_delete=models.PROTECT)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.FloatField()
    status = models.CharField(
        max_length=15, choices=StatusType.choices, default="pending"
    )

    class Meta:
        ordering = ["-created_at"]
        db_table = "cash_transaction"
        indexes = [models.Index(fields=["-created_at"]), models.Index(fields=["type"])]

    def __str__(self):
        return f"{self.account.name} - {self.created_at} -{self.type}"


class Transfer(BaseModel):
    source_account = models.ForeignKey(
        "Account", on_delete=models.PROTECT, related_name="source_account"
    )
    destination_account = models.ForeignKey(
        "Account", on_delete=models.PROTECT, related_name="destination_account"
    )
    amount = models.FloatField()
    time = models.DateTimeField(default=datetime.now())
    status = models.CharField(
        max_length=15, choices=StatusType.choices, default="pending"
    )

    class Meta:
        ordering = ["-created_at"]
        db_table = "transfers"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["amount"]),
        ]

    def __str__(self):
        return f"{self.source_account.name} to {self.destination_account.name}"


class TransactionHistory(BaseModel):
    class TransactionType(models.TextChoices):
        DEBIT = "debit", ("debit")
        CREDIT = "credit", ("credit")

    account = models.ForeignKey(
        "Account", on_delete=models.PROTECT, related_name="account"
    )
    old_balance = models.FloatField()
    amount = models.FloatField()
    new_balance = models.FloatField()
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    transfer_account = models.ForeignKey(
        "Account",
        related_name="transfer_account",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        db_table = "histories"
        verbose_name = "Transaction Historie"
        indexes = [models.Index(fields=["-created_at"]), models.Index(fields=["type"])]

    def __str__(self):
        return f"{self.account.name}"
