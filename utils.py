from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError

class SignUpForm(FlaskForm):
    name = StringField('Full Name', 
                        validators=[InputRequired(), 
                                    Length(min=2, max=70)],
                        render_kw={"placeholder": "Enter full name"})
    origin = StringField('Place of origin', 
                        validators=[InputRequired(), 
                                    Length(min=2, max=255)],
                        render_kw={"placeholder": "Enter country of origin"})
    email = StringField('Email address', 
                        validators=[InputRequired(), 
                                    Email(message="Invalid email address"), 
                                    Length(min=3, max=255)],
                        render_kw={"placeholder": "Enter email"})
    password = PasswordField('Password', 
                        validators=[InputRequired(), 
                                    EqualTo('confirm', message='Passwords must match'), 
                                    Length(min=4, max=12)],
                        render_kw={"placeholder": "Enter password"})
    confirm = PasswordField('Confirm password',
                        render_kw={"placeholder": "Confirm your password"})
                        
class LoginForm(FlaskForm):
    email = StringField('Email address', 
                        validators=[InputRequired(), 
                                    Email(message="Invalid email address"), 
                                    Length(min=3, max=255)],
                        render_kw={"placeholder": "Enter email"})
    password = PasswordField('Password', 
                        validators=[InputRequired(), 
                                    Length(min=4, max=12)],
                        render_kw={"placeholder": "Enter password"})
    remember = BooleanField("Remember me")