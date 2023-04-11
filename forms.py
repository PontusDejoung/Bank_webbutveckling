from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, ValidationError,EmailField
from wtforms.fields import IntegerField, SelectField, DateField, PasswordField
from wtforms.validators import Email, InputRequired, EqualTo



def checkName(form,field):
    min=3
    length = field.data and len(field.data) or 0
    if length < min:
        raise ValidationError('Måste minst vara 3 tecken långt')

def checkNationalid(form,field):
    if field.data.strip().isdigit() == False:
        raise ValidationError("Please type only numbers")
    if len(field.data) < 12 or len(field.data) > 12:
        raise ValidationError("National id must contain 12 numbers")
def checkTelephoneNr(form,field):
    if field.data.strip().isdigit() == False:
        raise ValidationError("Please type only numbers")

class DepositOrWithdraw(FlaskForm):
    type = SelectField("Select Type", [validators.DataRequired(message="Please Select One")], choices=[("Deposit"),("Withdraw")])
    amount = IntegerField("Amount",[validators.NumberRange(min=1),validators.DataRequired(message="Enter amount")])

class TransferForm(FlaskForm):
    Receiver = IntegerField("Send to",[validators.NumberRange(min=1), validators.DataRequired(message="Enter Account Number For Receiver")])
    Amount = IntegerField("Amount",[validators.NumberRange(min=1),validators.DataRequired(message="Enter Amount")])

class NewCustomer(FlaskForm):
    firstName = StringField('First Name', validators=[validators.Length(min=3), validators.DataRequired()])
    lastName = StringField('Last Name', validators=[validators.Length(min=3), validators.DataRequired()])
    adress = StringField('Adress', validators=[validators.Length(min=1),validators.DataRequired()])
    city = StringField('City', validators=[validators.Length(min=2), validators.DataRequired()])
    zipcode = IntegerField('Zipcode', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    country = SelectField('Country', [validators.DataRequired("Please Select One")],choices=[('Sweden'),('Norway'),('Finland'),('Denmark'),('USA')])
    countryCode = SelectField('Country Code', [validators.DataRequired("Please Select One")],choices=[('SE'),('NO'),('FI'),('DK'),('US')])
    birthDate = DateField('Birth Date', validators=[validators.DataRequired("Please Enter Birth date")])
    nationalId = StringField('National Id', validators=[validators.DataRequired(), checkNationalid])
    telephoneCountryCode = SelectField('Telephone Country Code',[validators.DataRequired("Please Select One")],choices=[('+46'),('+47'),('+358'),('+45'),('+1'),('+55')])
    telephoneNr = StringField('Telephone Number', validators=[validators.DataRequired(), checkTelephoneNr])
    email = StringField('Email Adress', validators=[validators.DataRequired(),Email("This field requires a valid email adress")])

class NewUserForm(FlaskForm):
    email = StringField('Email Adress', validators=[validators.DataRequired(),Email("This field requires a valid email")])
    password = PasswordField('Password',[validators.DataRequired("Please enter a password"),validators.Length(min=6),EqualTo('confirm',message=("Password do not match"))])
    confirm = PasswordField('Repeat Password')
    role = SelectField("Select roles",[validators.DataRequired(message="Pleases select one")], choices=[('Admin'),('Cashier')])

class editUser(FlaskForm):
    role = SelectField("Select Type", [validators.DataRequired(message="Please select one")], choices=[("Cashier"),("Admin")])

class ForgotForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired(), Email("This field requires a valid email")])

class ResetPasswordForm(FlaskForm):
    newpassword = PasswordField('Password',[validators.DataRequired("Please enter a password"),validators.Length(min=6),EqualTo('confirmpassword',message=("Password do not match"))])
    confirmpassword = PasswordField('Repeat Password')