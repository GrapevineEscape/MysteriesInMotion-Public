from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

class ShowForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    type = SelectField('Type', choices=[('Standard', 'Standard'), ('Escape', 'Escape'), ('Online Mystery', 'Online Mystery')], validators=[DataRequired()])
    kid_friendly = BooleanField('Kid-Friendly')
    script = FileField('Upload Script (PDF)')
    image = FileField('Upload Image (PNG)')
    submit = SubmitField('Add Show')

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired(), Length(max=50)])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('Any', 'Any')], validators=[DataRequired()])
    age = StringField('Age Range', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Role Description', validators=[DataRequired()])
    submit = SubmitField('Save Role')
