from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, SubmitField, PasswordField, RadioField, BooleanField
from wtforms.validators import InputRequired, EqualTo, Length

class RegistrationForm(FlaskForm):
    user_id = StringField("User id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Repeat password:", 
                validators=[InputRequired(),EqualTo("password")])
    submit = SubmitField("Submit")
    
class LoginForm(FlaskForm):
    user_id = StringField("User id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")
    
class applyForm(FlaskForm):
    firstName = StringField("Please enter your first name",
                            validators=[InputRequired()])
    lastName = StringField("Please enter your last name",
                           validators=[InputRequired()])
    address = StringField("Please enter your home address", validators=[InputRequired()])
    reason = StringField("Please tell us why you wanna apply for adoption", validators=[InputRequired()])
    submit = SubmitField("Submit")
    
class filterForm(FlaskForm):
    speciesFilter = RadioField('Select by:', choices=['dog','cat','all'])
    submit = SubmitField("submit")
   
 
class volunteerForm(FlaskForm):
    reason = StringField("Why would you like to volunteer?", validators=[InputRequired(), Length(min=10, max=500)])
    submit = SubmitField("submit")
    
class manageForm(FlaskForm):
    application_filter = RadioField('Select by:', choices=['Submitted','Processing','Completed'])
    submit = SubmitField("Submit")
    
class reviewForm(FlaskForm):
    review = StringField("Leave a review", validators=[InputRequired()])
    submit = SubmitField("submit")