from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SuggestCafeForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    map_url = StringField('Google Maps URL', validators=[Optional(), URL()])
    img_url = StringField('Image URL', validators=[Optional(), URL()])
    location = StringField('Location (e.g., City, Address)', validators=[DataRequired()])
    has_sockets = BooleanField('Has Sockets?')
    has_toilet = BooleanField('Has Toilet?')
    has_wifi = BooleanField('Has Wifi?')
    can_take_calls = BooleanField('Can Take Calls?')
    seats = StringField('Number of Seats (e.g., 10-20, 50+)', validators=[Optional()])
    coffee_price = StringField('Coffee Price (e.g., $2.50)', validators=[Optional()])
    submit = SubmitField('Submit Suggestion')