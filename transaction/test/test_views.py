import json
from rest_framework import status
from django.test import TestCase, Client, SimpleTestCase, override_settings
from django.urls import reverse
from transaction.models import Account,Transfer,  CashTransaction, TransactionHistory
from transaction.serializers import AccountSerializer, AccountDetailSerializer, TransferSerializer, CashTransactionSerializer, TransactionHistorySerializer
from django.utils import timezone
from datetime import timedelta
from transaction.tasks.transfer import schedule_transfer
from celery import app
# initialize the APIClient app
client = Client()

class GetAllAccountsTest(TestCase):
    """ Test module for GET all Accounts API """

    def setUp(self):
        Account.objects.create(
            name='Omar', contact='01787553318', balance=1000 )
        Account.objects.create(
            name='Faruk', contact='01787553319', balance=1000)
        Account.objects.create(
            name='Musa', contact='01787553320', balance=1000)
        Account.objects.create(
            name='Abdullah', contact='01787553321', balance=1000)

    def test_get_all_accounts(self):
        # get API response
        response = client.get(reverse('list_create_accounts'))
        # get data from db
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetSingleAccountsTest(TestCase):
    """ Test module for GET Single Account API """

    def setUp(self):
        self.omar = Account.objects.create(
            name='Omar', contact='01787553318', balance=1000 )
        self.faruk = Account.objects.create(
            name='Faruk', contact='01787553319', balance=1000)
        self.musa = Account.objects.create(
            name='Musa', contact='01787553320', balance=1000)
        self.abdullah = Account.objects.create(
            name='Abdullah', contact='01787553321', balance=1000)

    def test_get_valid_single_account(self):
        # get API response
        response = client.get(reverse('get_update_account', kwargs={'id':  self.musa.id}))
        # get data from db
        account = Account.objects.get(id = self.musa.id)
        serializer = AccountDetailSerializer(account)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_invalid_single_account(self):
        # get API response
        response = client.get( reverse('get_update_account', kwargs={'id': 3000}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CreateNewAccountTest(TestCase):
    """ Test module for inserting a new account """

    def setUp(self):
        self.valid_payload =  {
        "name": "Omar",
        "contact": "01787553312",
        "balance" : 200.00
        }
        self.invalid_payload_contact_repeat = {
        "name": "Omar",
        "contact": "01787553318",
        "balance" : 200.00
        }


        self.invalid_payload_negative_balance = {
               "name":'Omar',
        "contact":'01787553328',
        "balance": -1000 
        }
    

    def test_create_a_valid_account(self):
        response = client.post(
            reverse('list_create_accounts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_account_contact_repeat(self):
        Account.objects.create(
            name='Omar', contact='01787553318', balance=1000 )
        response = client.post(
            reverse('list_create_accounts'),
            data=json.dumps(self.invalid_payload_contact_repeat),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_account_negative_balance(self):
        response = client.post(
            reverse('list_create_accounts'),
            data=json.dumps(self.invalid_payload_negative_balance),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UpdateSingleAccountTest(TestCase):
    """ Test module for updating an existing account record """

    def setUp(self):
        self.omar = Account.objects.create(
            name='Omar', contact='01787553318', balance=1000 )
        self.faruk = Account.objects.create(
            name='Faruk', contact='01787553319', balance=1000)
        self.musa = Account.objects.create(
            name='Musa', contact='01787553320', balance=1000)
        self.abdullah = Account.objects.create(
            name='Abdullah', contact='01787553321', balance=1000)

        self.valid_payload ={"balance" : 500.0}
        self.invalid_payload_contact_repeat = {"contact": self.omar.contact}
        self.invalid_payload_negative_balance = {"balance": -1000 }

    def test_valid_update_account(self):
        response = client.patch(
            reverse('get_update_account', kwargs={"id": self.omar.id}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 500)
        


    def test_invalid_update_account_contact_repeat(self):
        response = client.patch(
            reverse('get_update_account',kwargs={"id": self.omar.id}),
            data=json.dumps(self.invalid_payload_contact_repeat),
            content_type='application/json'
        )
        print(response.json())
        print(self.omar)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_invalid_update_account_negative_balance(self):
        response = client.patch(
            reverse('get_update_account',kwargs={"id": self.omar.id}),
            data=json.dumps(self.invalid_payload_negative_balance),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CreateNewTransferTest(TestCase):
    """ Test module for inserting a new transfer """

    def setUp(self):
        self.transfer_time = timezone.now()+timedelta(seconds=10)
        self.omar = Account.objects.create(name='Omar', contact='01787553318', balance=1000 )
        self.faruk = Account.objects.create(name='Faruk', contact='01787553319', balance=1000)
        self.musa = Account.objects.create(name='Musa', contact='01787553320', balance=1000)
        self.abdullah = Account.objects.create(name='Abdullah', contact='01787553321', balance=1000)

        self.valid_payload = [

    {
        "source_account": self.omar.id,
        "destination_account": self.musa.id,
        "amount": 100,
        "time" :"2020-07-04 23:18:50+06:00"
    
    },
    {
        "source_account": self.faruk.id,
        "destination_account": self.abdullah.id,
        "amount": 100,
        "time" :"2020-07-04 23:18:50+06:00"
    
    }
    ]
        self.invalid_payload_same_account =     [
        {
        "source_account": self.faruk.id,
        "destination_account": self.faruk.id,
        "amount": 100,
        "time" :"2020-07-04 23:18:50+06:00"
    
    }]


        self.invalid_payload_negative_amount = [
        {
        "source_account": self.faruk.id,
        "destination_account": self.abdullah.id,
        "amount": -100,
        "time" :"2020-07-04 23:18:50+06:00"
    
    }]


        self.invalid_payload_balance_shortage = [
        {
        "source_account": self.faruk.id,
        "destination_account": self.abdullah.id,
        "amount": self.faruk.balance + 0.5,
        "time" :"2020-07-04 23:18:50+06:00"
    
    }]

        self.schedule_transfer_payload = [{
            "source_account": self.omar.id,
            "destination_account": self.musa.id,
            "amount": 312.25,
            "time" : str(self.transfer_time)
    }]
        
        

    def test_create_a_valid_transfer(self):
        omar_old_balance = self.omar.balance
        musa_old_balance = self.musa.balance
        amount = 100
        old_history_length = (len(TransactionHistory.objects.all()))
        response = client.post(
            reverse('list_create_transfers'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        
        omar_new_balance = Account.objects.get(name='Omar').balance
        musa_new_balance = Account.objects.get(name='Musa').balance
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #check balance update
        self.assertEqual((omar_old_balance - omar_new_balance),amount)
        self.assertEqual((musa_new_balance - musa_old_balance),amount)
        #check if a history is created
        new_history_length = (len(TransactionHistory.objects.all()))
        # new transaction = transfer number(*2)
        self.assertEqual((new_history_length - old_history_length),4)


        

    def test_create_invalid_transfer_to_same_account(self):
        response = client.post(
            reverse('list_create_transfers'),
            data=json.dumps(self.invalid_payload_same_account),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_transfer_negative_balance(self):
        response = client.post(
            reverse('list_create_transfers'),
            data=json.dumps(self.invalid_payload_negative_amount),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def create_invalid_transfer_balance_shortage(self):
        response = client.post(
            reverse('list_create_transfers'),
            data=json.dumps(self.invalid_payload_balance_shortage),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_create_a_schedule_transfer(self):
        musa_old_balance = self.musa.balance
        omar_old_balance = self.omar.balance
        amount = self.schedule_transfer_payload[0]['amount']
        old_history_length = (len(TransactionHistory.objects.all()))
        
        response = client.post(
            reverse('list_create_transfers'),
            data=json.dumps(self.schedule_transfer_payload),
            content_type='application/json'
        )
        while timezone.now()>(self.transfer_time+timedelta(seconds = 6)):

            musa_new_balance = Account.objects.get(name='Musa').balance
            omar_new_balance = Account.objects.get(name='Omar').balance
            
            #check balance update
            self.assertEqual((omar_old_balance - omar_new_balance),amount)
            self.assertEqual((musa_new_balance - musa_old_balance),amount)
            #check if a history is created
            new_history_length = (len(TransactionHistory.objects.all()))
            # new transaction = transfer number(*2)
            self.assertEqual((new_history_length - old_history_length),2)
            break
