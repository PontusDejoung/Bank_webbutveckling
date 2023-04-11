from flask import Flask, render_template, request, redirect,flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import functions
from flask_migrate import Migrate, upgrade
import operator
from sqlalchemy import func
from model import db, seedData1,seedData2,Customer,Account,Transaction, user_datastore,User
from forms import DepositOrWithdraw, NewCustomer, TransferForm, NewUserForm,editUser, ForgotForm,ResetPasswordForm
from api import api
from flask_security import Security,roles_accepted, auth_required, logout_user
from datetime import datetime,timedelta
import os
from flask_security import auth_required, hash_password
from flask_mail import Mail,Message



app = Flask(__name__)
app.config.from_object('config.ConfigDebug')
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
app.security = Security(app, user_datastore)
mail = Mail(app)



app.register_blueprint(api, url_prefix="/")


@app.route("/", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin","Cashier")
def startPage():
    customerBalance = Account.query.all()
    accountBalance = 0
    for account in customerBalance:
        accountBalance += account.Balance
    customer = Customer.query.all()
    totalCustomers = 0
    for customers in customer:
        totalCustomers += 1
    searchWithId = request.form.get("customerId")

    if searchWithId:
        if searchWithId.strip().isdigit() != True:
            flash(f"Please type only numbers")
            return redirect(url_for('startPage'))
        searchForCustomer = Customer.query.filter_by(Id=searchWithId).first()
        if searchForCustomer == None:
            flash(f"Do not exist any customer withd id:{searchWithId}")
            return redirect(url_for('startPage'))
        return redirect(url_for("customerPage", id=searchWithId))
    queryCustomerByCountry = db.session.query(Customer.Country, functions.count(Customer.Country)).group_by(Customer.Country).all()
    queryAccountBalanceByCountry = db.session.query(functions.count(Account.CustomerId), functions.sum(Account.Balance)).join(Customer).group_by(Customer.Country).all()
    resultCustomerQuery = zip(queryCustomerByCountry,queryAccountBalanceByCountry)
    return render_template("startPage.html",
                            resultCustomerQuery=resultCustomerQuery,
                            totalCustomers=totalCustomers, accountBalance=accountBalance)

@app.route("/countryside/<id>")
@auth_required()
@roles_accepted("Admin","Cashier")
def countryside(id):
    topEarnersInCountry = db.session.query(Customer.Id, functions.sum(Account.Balance)).join(Account).filter(Customer.Country==id).group_by(Customer.Id).all()
    topEarnersInCountry.sort(key=operator.itemgetter(1), reverse=True)
    topEarnersInCountry = topEarnersInCountry[:10]
    sortedList = []
    for customer in topEarnersInCountry:
        getCustomerObject = Customer.query.filter(Customer.Id == customer[0]).first()
        sortedList.append((getCustomerObject, customer[1]))
    return render_template("countrySide.html", sortedList=sortedList, id=id)
@app.route("/admin")
@auth_required()
@roles_accepted("Admin")
def admin():
    render_template("admin.html", activePage="secretPage")

@app.route("/customers")
@auth_required()
@roles_accepted("Admin","Cashier")
def customers():
    sortColumn = request.args.get('sortColumn', 'name')
    sortOrder = request.args.get('sortOrder', 'asc')
    searchWord = request.args.get('q','')
    page = int(request.args.get('page', 1))

    listofCustomers = Customer.query.filter(        
        Customer.GivenName.like('%' + searchWord + '%')| 
        Customer.Surname.like('%' + searchWord + '%')| 
        Customer.City.like('%' + searchWord + '%')| 
        Customer.Id.like('%' + searchWord + '%')| 
        Customer.Streetaddress.like('%' + searchWord + '%')| 
        Customer.NationalId.like('%' + searchWord + '%'))
    
    if sortColumn == "name":
        if sortOrder == "asc":
            listofCustomers = listofCustomers.order_by(Customer.GivenName.asc())
        else:  
            listofCustomers = listofCustomers.order_by(Customer.GivenName.desc())

    elif sortColumn == "city":
        if sortOrder == "asc":
            listofCustomers = listofCustomers.order_by(Customer.City.asc())
        else:
            listofCustomers = listofCustomers.order_by(Customer.City.desc())
    elif sortColumn == "id":
        if sortOrder == "asc":
            listofCustomers = listofCustomers.order_by(Customer.Id.asc())
        else:
            listofCustomers = listofCustomers.order_by(Customer.Id.desc())

    elif sortColumn == "streetaddress":
        if sortOrder == "asc":
            listofCustomers = listofCustomers.order_by(Customer.Streetaddress.asc())
        else:
            listofCustomers = listofCustomers.order_by(Customer.Streetaddress.desc())
    
    elif sortColumn == "nationalid":
        if sortOrder == "asc":
            listofCustomers = listofCustomers.order_by(Customer.NationalId.asc())
        else:
            listofCustomers = listofCustomers.order_by(Customer.NationalId.desc())

    
    paginationObject = listofCustomers.paginate(page=page, per_page=50, error_out=False)

    return render_template("customers.html", 
                            listOfCustomers=paginationObject.items,
                            pages = paginationObject.pages,
                            sortOrder=sortOrder,
                            page=page,
                            has_next=paginationObject.has_next,
                            has_prev=paginationObject.has_prev,
                            sortColumn=sortColumn,
                            q=searchWord )

@app.route("/customerpage/<id>")
@auth_required()
@roles_accepted("Admin","Cashier")
def customerPage(id):
    customer = Customer.query.filter_by(Id=id).first()
    specifiedAccounts = Account.query.filter(Account.CustomerId==customer.Id).all()
    totalBalance = 0
    for money in specifiedAccounts:
        totalBalance += money.Balance
    return render_template("customerInfo.html",
                            customer=customer,
                            specifiedAccounts=specifiedAccounts,
                            totalBalance=totalBalance
    )

@app.route("/account/<id>")
@auth_required()
@roles_accepted("Admin","Cashier")
def account(id):
    account = Account.query.filter_by(Id=id).first()
    transaction = Transaction.query.filter(Transaction.AccountId==id).order_by(Transaction.Date.desc())
    transaction = transaction.order_by(Transaction.Date.desc())
    page = int(request.args.get('page', 1))

    paginationObject = transaction.paginate(page=page, per_page=20, error_out=False)

    return render_template("account.html",
                            account=account,
                            # transaction=transaction,
                            transaction=paginationObject.items,
                            pages = paginationObject.pages,
                            page=page,
                            has_next=paginationObject.has_next,
                            has_prev=paginationObject.has_prev
    )

@app.route("/newcustomer", methods=['GET', 'POST'])
def newCustomer():
    form = NewCustomer()
    validation = True
    hash = ""
    if request.method == "POST":
        hash = form.nationalId.data
        hash = hash[:8] + '-' + hash[8:]
        checkIfNationalIdAlreadyExist = Customer.query.filter(Customer.NationalId==hash).first()
        if checkIfNationalIdAlreadyExist !=  None:
            form.nationalId.errors = form.nationalId.errors + ('User with this national id already exist',)
            validation = False
    if validation and form.validate_on_submit():
        newcustomer = Customer()
        newcustomer.GivenName = form.firstName.data
        newcustomer.Surname = form.lastName.data
        newcustomer.Streetaddress = form.adress.data
        newcustomer.City = form.city.data
        newcustomer.Zipcode = form.zipcode.data
        newcustomer.Country = form.country.data
        newcustomer.CountryCode = form.countryCode.data
        newcustomer.Birthday = form.birthDate.data
        newcustomer.NationalId = hash
        newcustomer.TelephoneCountryCode = form.telephoneCountryCode.data
        newcustomer.Telephone = form.telephoneNr.data
        newcustomer.EmailAddress = form.email.data
        db.session.add(newcustomer)
        db.session.commit()
        account = Account()
        customerId = Customer.query.filter(Customer.NationalId==hash).first()
        account.AccountType = "Personal"
        account.Balance = 0
        account.Created = datetime.now()
        account.CustomerId = customerId.Id
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('startPage'))
    return render_template("createCustomer.html", theForm=form)
@app.route("/editcustomer/<int:id>", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Cashier")
def editcustomer(id):
    customer = Customer.query.filter_by(Id=id).first()
    form = NewCustomer()
    if form.validate_on_submit():
        customer.GivenName = form.firstName.data
        customer.Surname = form.lastName.data
        customer.Streetaddress = form.adress.data
        customer.City = form.city.data
        customer.Zipcode = form.zipcode.data
        customer.Country = form.country.data
        customer.CountryCode = form.countryCode.data
        customer.Birthday = form.birthDate.data
        customer.NationalId = form.nationalId.data
        customer.TelephoneCountryCode = form.telephoneCountryCode.data
        customer.Telephone = form.telephoneNr.data
        customer.EmailAddress = form.email.data
        db.session.commit()
        return redirect("/customers")
    if request.method == 'GET':
        form.firstName.data = customer.GivenName
        form.lastName.data = customer.Surname
        form.adress.data = customer.Streetaddress
        form.city.data = customer.City
        form.zipcode.data = customer.Zipcode
        form.country.data = customer.Country
        form.countryCode.data = customer.CountryCode
        form.birthDate.data = customer.Birthday
        form.nationalId.data = customer.NationalId
        form.telephoneCountryCode.data = customer.TelephoneCountryCode
        form.telephoneNr.data = customer.Telephone
        form.email.data = customer.EmailAddress
    return render_template("editcustomer.html", theForm=form)

@app.route("/adduser", methods=["POST","GET"])
@auth_required()
@roles_accepted("Admin")
def addUser():
    form = NewUserForm()
    validation = True
    if request.method == "POST":
        checkifUserAlreadyExist = user_datastore.find_user(email=form.email.data)
        if checkifUserAlreadyExist != None:
            form.email.errors = form.email.errors + ('User Already Exist',)
            validation = False
    if validation and form.validate_on_submit():
        checkifUserAlreadyExist = user_datastore.find_user(email=form.email.data)
        newUser = user_datastore.create_user(email=form.email.data, 
                                            password=hash_password(form.confirm.data),
                                            roles=[form.role.data])
        db.session.add(newUser)
        db.session.commit()
        flash("User Created")
        return redirect(url_for("startPage"))
    return render_template("createUser.html",form=form)

@app.route("/users",methods=["POST","GET"])
@auth_required()
@roles_accepted("Admin")
def users():
    sortColumn = request.args.get('sortColumn', 'email')
    sortOrder = request.args.get('sortOrder', 'asc')
    searchWord = request.args.get('q','')
    page = int(request.args.get('page', 1))
    
    listofUsers = User.query.filter(        
        User.email.like('%' + searchWord + '%'))
    
    if sortColumn == "email":
        if sortOrder == "asc":
            listofUsers = listofUsers.order_by(User.email.asc())
        else:  
            listofUsers = listofUsers.order_by(User.email.desc())
   
    paginationObject = listofUsers.paginate(page=page, per_page=50, error_out=False)
    return render_template("users.html", listofUsers=paginationObject,pages=paginationObject.pages,
                                        sortOrder=sortOrder,page=page,has_next=paginationObject.has_next,
                                        has_prev=paginationObject.has_prev,sortColumn=sortColumn,q=searchWord)

@app.route("/addRole/<id>",methods=["POST","GET"])
@auth_required()
@roles_accepted("Admin")
def addRole(id):
    form = editUser()
    findUser = user_datastore.find_user(id=id)
    if form.validate_on_submit():
        if len(findUser.roles) >= 1:
            flash("User already have a role")
            return redirect(url_for('addRole', id=id))
        user_datastore.commit()
        newRole = user_datastore.add_role_to_user(user=findUser, role=form.role.data)
        user_datastore.commit()
        if newRole == False:
            flash("User already have this role")
            return redirect(url_for('addRole',id=id))
        return redirect(url_for('users'))
    if request.method == "GET":
        form.role.data = findUser.roles
    return render_template("editUser.html", form=form)


@app.route("/transaction/<id>", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin","Cashier")
def transaction(id):
    depositOrWithdraw = True
    account = Account.query.filter_by(Id=id).first()
    form = DepositOrWithdraw(request.form)
    validation = True
    if request.method == 'POST':
        if form.type.data == "Withdraw" and form.amount.data > account.Balance:
            form.amount.errors = form.amount.errors + ('Your balance is to low',)
            validation = False
        if form.amount.data < 0:
            form.amount.errors = form.amount.errors + ('Amount must be bigger than 0',)
            validation = False
    if form.type.data == "Deposit":
        if validation and form.validate_on_submit():
            amount = form.amount.data
            account.Balance += amount
            depositTransaction = Transaction()
            depositTransaction.AccountId = account.Id
            depositTransaction.Amount = amount
            depositTransaction.Date = datetime.now()
            depositTransaction.NewBalance = account.Balance
            depositTransaction.Operation = "Deposit Cash"
            depositTransaction.Type = "Debit"
            db.session.add(depositTransaction)
            db.session.commit()
            return redirect(url_for('account', id=account.Id))
    if form.type.data == "Withdraw":
        if validation and form.validate_on_submit():
            amount = form.amount.data
            account.Balance -= amount
            withdrawTransaction = Transaction()
            withdrawTransaction.AccountId = account.Id
            withdrawTransaction.Amount = amount
            withdrawTransaction.Date = datetime.now()
            withdrawTransaction.NewBalance = account.Balance
            withdrawTransaction.Operation = "Bank Withdrawal"
            withdrawTransaction.Type = "Credit"
            db.session.add(withdrawTransaction)
            db.session.commit()
            return redirect(url_for('account', id=account.Id))
    return render_template("transaction.html", form=form, depositOrWithdraw=depositOrWithdraw,
                                                account=account)

@app.route("/transfer/<id>", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin","Cashier")
def transfer(id):
    transferValue = True
    form = TransferForm(request.form)
    getReceivingAccount = Account.query.filter_by(Id=form.Receiver.data).first()
    getTransferingAccount = Account.query.filter_by(Id=id).first()
    validation = True
    if request.method == "POST":
        if form.Amount.data > getTransferingAccount.Balance:
            form.Amount.errors = form.Amount.errors + ('Your balance is to low',)
            validation = False
        if getReceivingAccount == None:
            form.Receiver.errors = form.Receiver.errors + ('Receiving account do not exist',)
            validation = False
        if form.Receiver.data == getTransferingAccount.Id:
            form.Receiver.errors = form.Receiver.errors + ('You can not transfer from your account to same account',)
            validation = False
    if validation and form.validate_on_submit():
        amount = form.Amount.data
        getTransferingAccount.Balance -= amount
        transferingTransaction = Transaction()
        transferingTransaction.AccountId = getTransferingAccount.Id
        transferingTransaction.Amount = f"-{amount}"
        transferingTransaction.Date = datetime.now()
        transferingTransaction.NewBalance = getTransferingAccount.Balance
        transferingTransaction.Operation = "Transfer"
        transferingTransaction.Type = "Debit"
        db.session.add(transferingTransaction)
        db.session.commit()
        receivingAmount = form.Amount.data
        getReceivingAccount.Balance += receivingAmount
        receivingTransaction = Transaction()
        receivingTransaction.AccountId = getReceivingAccount.Id
        receivingTransaction.Amount = receivingAmount
        receivingTransaction.Date = datetime.now()
        receivingTransaction.NewBalance = getReceivingAccount.Balance
        receivingTransaction.Operation = "Transfer"
        receivingTransaction.Type = "Debit"
        db.session.add(receivingTransaction)
        db.session.commit()
        return redirect(url_for('account', id=id))
    return render_template("transaction.html", form=form, transferValue=transferValue, 
                            getTransferingAccount=getTransferingAccount)
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/resetpassword", methods=['GET','POST'])
def resetpassword():
    form = ForgotForm()
    validation = True
    if request.method == "POST":
        finduser = user_datastore.find_user(email=form.email.data)
        if finduser == None:
            form.email.errors = form.email.errors + ('No user with the given email exist',)
            validation = False
        if validation == True:
            code = finduser.get_auth_token()
            finduser.mf_recovery_codes = [code]
            user_datastore.commit()
        if validation and form.validate_on_submit():
            flash(f"Reset instructions will be sent to {form.email.data}")
            #!!Har använt mina fria antal mail i mailtrapen så den kraschar om jag inte kommenterar bort det
            # msg = Message('Reset Password', sender='fakebank@testbanken.se',recipients=[f'{form.email.data}'])
            # msg.body = render_template("/security/mail_reset.html",code=code,user=user)
            # mail.send(msg)
            return redirect(url_for('resetpassword'))
    return render_template("/security/forgot_password.html", form=form)

@app.route("/forgotenpassword/<userid>/<code>", methods=['GET','POST'])
def forgotenpassword(userid,code):
    form = ResetPasswordForm()
    if request.method == "GET":
        checkIfUserExist = user_datastore.find_user(id=userid)
        if checkIfUserExist.mf_recovery_codes != [code]:
            return redirect(url_for("startPage"))   
        checkIfUserExist.mf_recovery_codes = None
        user_datastore.commit()
    if form.validate_on_submit():
        getUser = user_datastore.find_user(id=userid)
        getUser.password = hash_password(form.newpassword.data)
        db.session.commit()
        flash("New password is set")
        return redirect(url_for('startPage'))
    return render_template("/security/new_password.html", form=form)
           
   

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seedData1(db)
        seedData2(app, db)
        app.run()

