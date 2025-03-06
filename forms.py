# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField,RadioField
from wtforms.validators import DataRequired,Regexp,Length , EqualTo, ValidationError
from models import CarrierName
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=64, message='Username must be between 4 and 64 characters.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
        
class ClientNumberForm0(FlaskForm):
    mobile_carrier = RadioField('Select Carrier', choices=[(carrier.name, carrier.value) for carrier in CarrierName], validators=[DataRequired()])
    next = SubmitField('Next')
    
class ClientNumberForm(FlaskForm):
    number = StringField('Enter Your Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Calling(FlaskForm):
    number = StringField('Enter Your Number', validators=[DataRequired()])
    submit = SubmitField('إرسال')

class selectMoney(FlaskForm):
    money= SelectField('Select an option', choices=[(10, 10),(20, 20),(30, 30),(40, 40),(50, 50),(60, 60),(70,70)], validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class AddOfferForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    code = StringField('code', validators=[DataRequired(),Regexp(r'^[a-zA-Z0-9#*]+$', message="Invalid characters.")])
    mobile_carrier = SelectField('Select an option', choices=[(carrier.name, carrier.value) for carrier in CarrierName], validators=[DataRequired()])
    submit = SubmitField('Submit')

    