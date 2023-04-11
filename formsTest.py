import unittest
from app import app
from model import db,Account
import datetime


class FormsTestCases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(FormsTestCases, self).__init__(*args, **kwargs)
        self.ctx = app.app_context()
        self.ctx.push()
        #self.client = app.test_client()
        app.config["SERVER_NAME"] = "fakebank.se"
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(app)
        db.app = app
        db.create_all()
        
    def tearDown(self):
        #self.ctx.pop()
        pass

#Måste kommentera bort @auth_required och @roles_accepted i app.py 
# och måste ta bort current user i baseTemplate.html för att de ska funka

    def test_when_withdrawing_is_larger_then_balance(self):
        account = Account()
        account.AccountType = "Personal"
        account.Balance = 30
        account.Created = datetime.datetime.now()
        account.CustomerId = 1
        db.session.add(account)
        db.session.commit()
        test_client = app.test_client()
        with test_client:
            url = '/transaction/1'
            response = test_client.post(url, data={ "type":"Withdraw","amount":"31"})
            s = response.data.decode("UTF-8") 
            ok = 'Your balance is to low' in s
            self.assertTrue(ok)

    def test_when_transfer_amount_is_larger_then_balance(self):
        account = Account()
        account.AccountType = "Personal"
        account.Balance = 30
        account.Created = datetime.datetime.now()
        account.CustomerId = 2
        db.session.add(account)
        db.session.commit()
        account = Account()
        account.AccountType = "Personal"
        account.Balance = 30
        account.Created = datetime.datetime.now()
        account.CustomerId = 1
        db.session.add(account)
        db.session.commit()
        test_client = app.test_client()
        with test_client:
            url = '/transfer/1'
            response = test_client.post(url, data={ "Receiver":"2","Amount":"31"})
            s = response.data.decode("utf-8") 
            ok = 'Your balance is to low' in s
            self.assertTrue(ok)
    
    def test_when_withdraw_amount_is_negative(self):
        account = Account()
        account.AccountType = "Personal"
        account.Balance = 30
        account.Created = datetime.datetime.now()
        account.CustomerId = 1
        db.session.add(account)
        db.session.commit()
        test_client = app.test_client()
        with test_client:
            url = '/transaction/1'
            response = test_client.post(url, data={ "type":"Withdraw","amount":"-31"})
            s = response.data.decode("utf-8") 
            ok = 'Amount must be bigger than 0' in s
            self.assertTrue(ok)
    
    def test_when_deposit_amount_is_negative(self):
        account = Account()
        account.AccountType = "Personal"
        account.Balance = 30
        account.Created = datetime.datetime.now()
        account.CustomerId = 1
        db.session.add(account)
        db.session.commit()
        test_client = app.test_client()
        with test_client:
            url = '/transaction/1'
            response = test_client.post(url, data={ "type":"Deposit","amount":"-31"})
            s = response.data.decode("utf-8") 
            ok = 'Amount must be bigger than 0' in s
            self.assertTrue(ok)




if __name__ == "__main__":
    unittest.main()