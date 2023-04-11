from flask import Blueprint,jsonify,request
from datetime import datetime
from model import Transaction, Account,Customer


api = Blueprint('api', __name__)

class CustomerApi:
    Id = 0
    FirstName = ""
    LastName = ""
    Streetaddress = ""
    City = ""
    Zipcode = ""
    Country = ""
    CountryCode = ""
    Birthday = datetime.utcnow
    NationailId = ""
    Telephone = ""
    TelephoneCountryCode = ""
    EmailAdress = ""

class AccountApi:
   Id = 0
   AccounType = ""
   Created = datetime.utcnow
   Balance = 0
   CustomerId = 0

class TransactionApi:
    Id = 0
    Type = ""
    Operation = ""
    Date = ""
    Amount = 0
    NewBalance = 0
    AccountId = 0

def mapTransactionApi(transaction):
    transactionApi = TransactionApi()
    transactionApi.Id = transaction.Id
    transactionApi.Amount = transaction.Amount
    transactionApi.Date = transaction.Date
    transactionApi.AccountId = transaction.AccountId
    transactionApi.NewBalance = transaction.NewBalance
    transactionApi.Operation = transaction.Operation
    transactionApi.Type = transaction.Type
    return transactionApi


def mapAccountApi(account):
    accountApiModel = AccountApi()
    accountApiModel.Id = account.Id
    accountApiModel.Balance = account.Balance
    accountApiModel.Created = account.Created
    accountApiModel.CustomerId = account.CustomerId
    accountApiModel.AccounType = account.AccountType
    return accountApiModel

def mapCustomerApi(customer):
    mapCustomerApi = CustomerApi()
    mapCustomerApi.Birthday = customer.Birthday
    mapCustomerApi.City = customer.City
    mapCustomerApi.Country = customer.Country
    mapCustomerApi.CountryCode = customer.CountryCode
    mapCustomerApi.EmailAdress = customer.EmailAddress
    mapCustomerApi.FirstName = customer.GivenName
    mapCustomerApi.LastName = customer.Surname
    mapCustomerApi.Id = customer.Id
    mapCustomerApi.NationailId = customer.NationalId
    mapCustomerApi.Streetaddress = customer.Streetaddress
    mapCustomerApi.Telephone = customer.Telephone
    mapCustomerApi.TelephoneCountryCode = customer.TelephoneCountryCode
    mapCustomerApi.Zipcode = customer.Zipcode
    return mapCustomerApi

def GetAccountDetails(id):
    account = Account.query.filter(Account.CustomerId == id).all()
    return account

def getCustomer(id):
    customer = Customer.query.filter(Customer.Id == id).first()
    return customer

def getTransactions(id):
    transaction = Transaction.query.filter(Transaction.AccountId == id).order_by(Transaction.Date.desc())
    return transaction


@api.route("/api/customer/<id>")
def customer(id):
    customer = getCustomer(id)
    CustomerApi = mapCustomerApi(customer)

    account = GetAccountDetails(id)
    accountList = []
    for accounts in account:
        accountApi = mapAccountApi(accounts)
        accountList.append(accountApi)
    return jsonify(CustomerApi.__dict__, [accounts.__dict__ for accounts in accountList])

@api.route("/api/accounts/<id>")
def accounts(id):
    accountTransactions = getTransactions(id)
    transactionList = []
    for transactions in accountTransactions:
        transactionApi = mapTransactionApi(transactions)
        transactionList.append(transactionApi)
    return jsonify([transactions.__dict__ for transactions in transactionList])

@api.route("/api/<id>/transaction")
def transactions(id):
    listWithTransactions = []
    transaction = getTransactions(id)
    page = int(request.args.get('page',2))
    paginationObject = transaction.paginate(page=page, per_page=20,error_out=False)
    hasNext = paginationObject.has_next
    for transactions in paginationObject.items:
        trans = {"Id":transactions.Id, "Date":transactions.Date,
                  "Operation":transactions.Operation, "Type":transactions.Type,
                    "Amount":transactions.Amount, "AccountId":transactions.AccountId,
                    "NewBalance":transactions.NewBalance}
        listWithTransactions.append(trans)
    return jsonify(listWithTransactions,hasNext)