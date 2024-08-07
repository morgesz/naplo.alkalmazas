# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired

class NaploForm(FlaskForm):
    datum = StringField('Dátum (YYYY-MM-DD)', validators=[DataRequired()])
    cim = StringField('Cím', validators=[DataRequired()])
    tartalom = TextAreaField('Tartalom', validators=[DataRequired()])
    submit = SubmitField('Mentés')

class ImportForm(FlaskForm):
    file = FileField('CSV Fájl', validators=[DataRequired()])
    submit = SubmitField('Importálás')
