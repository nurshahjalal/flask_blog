from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # these functions are called with the FlaskForm class that
    # our RegistrationForm class inherited from, they are automatically called
    # when form is submitted
    # inline = getattr(self.__class__, 'validate_%s' % name, None)
    # There is a lot going on in the background, but from what I can tell,
    # Flask is checking for extra functions created with the naming pattern:
    # "validate_(field name)", and later calling those extra functions

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username is Taken, Please choose another username")

    def validate_email(self, email):
        email_address = User.query.filter_by(email=email.data).first()
        if email_address:
            raise ValidationError('This email has been already used')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):

    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # This is for label and what type of file is allowed
    picture_file = FileField("Update Profile Image", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')

    # these functions are called with the FlaskForm class that
    # our RegistrationForm class inherited from, they are automatically called
    # when form is submitted
    # inline = getattr(self.__class__, 'validate_%s' % name, None)
    # There is a lot going on in the background, but from what I can tell,
    # Flask is checking for extra functions created with the naming pattern:
    # "validate_(field name)", and later calling those extra functions

    def validate_username(self, username):
        # check current user and requested username is same or not, user can submit same username to update
        if username.data != current_user.username:
            # if user requests another username to update, check requested username is available
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username is Taken, Please choose another username")

    def validate_email(self, email):
        # check current email and requested email is same or not, user can submit same email to update
        if email.data != current_user.email:
            email_address = User.query.filter_by(email=email.data).first()
            if email_address:
                raise ValidationError('This email has been already used')


