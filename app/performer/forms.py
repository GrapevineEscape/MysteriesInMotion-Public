from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

class PerformerProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    address = StringField('Address', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Regexp(r'^\d{10}$', message='Phone number must be 10 digits')])
    bio = TextAreaField('Short Bio', validators=[Optional(), Length(max=500)])
    headshot = FileField('Upload Headshot (PNG only)')
    submit = SubmitField('Update Profile')
