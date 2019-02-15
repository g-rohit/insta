from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo



class PasswordResetForm(FlaskForm):

    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')