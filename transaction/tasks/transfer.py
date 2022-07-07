from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.decorators import task
import os
from django.conf import settings
import requests
import json
from django.db import transaction
from transaction.models import Transfer, TransactionHistory, Account
from django.db.models import F

logger = get_task_logger(__name__)


# from celery.decorators import task


@task(name="schedule_transfer")
def schedule_transfer(transfer, source_account_old_balance):
    source_account_id = transfer["source_account"]
    amount = transfer["amount"]
    destination_account_id = transfer["destination_account"]
    destination_account = Account.objects.get(id=destination_account_id)
    destination_account_old_balance = destination_account.balance
    destination_account_new_balance = destination_account_old_balance + amount
    destination_account.balance = destination_account_new_balance
    source_account_new_balance = source_account_old_balance - amount

    history_destination = TransactionHistory(
        account_id=destination_account_id,
        transfer_account_id=source_account_id,
        amount=amount,
        type="credit",
        old_balance=destination_account_old_balance,
        new_balance=destination_account_new_balance,
    )
    history_source = TransactionHistory(
        account_id=source_account_id,
        transfer_account_id=destination_account_id,
        amount=amount,
        type="debit",
        old_balance=source_account_old_balance,
        new_balance=source_account_new_balance,
    )
    transfer["source_account_id"] = transfer.pop("source_account")
    transfer["destination_account_id"] = transfer.pop("destination_account")

    try:
        with transaction.atomic():
            destination_account.save()
            history_source.save()
            history_destination.save()
            transfer["status"] = "success"
            Transfer.objects.create(**transfer)

    except:
        Account.objects.filter(id=source_account_id).update(
            balance=F("balance") + transfer["amount"]
        )
        transfer["status"] = "aborted"
        Transfer.objects.create(**transfer)
