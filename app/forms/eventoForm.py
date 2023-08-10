from email.policy import default
from wtforms.widgets import TextArea
from wtforms import Form, StringField, SelectField, FileField
from wtforms.validators import DataRequired, InputRequired, Length
 
class EventoForm(Form):

    problema = StringField(
        'Qual o problema?',
        widget=TextArea(),
        render_kw={"placeholder": "Faça uma breve descrição do seu problema."},
        validators = [
            InputRequired(message=('*Campo Requerido')),
            Length(max=1000, message='A senha deve ter no mínimo %(max)d caracteres')
        ])

    endereco = StringField(
        'Qual o endereço da ocorrência:',
        render_kw={"placeholder": "Endereço da ocorrência."},
        validators = [
            InputRequired(message=('*Campo Requerido')),
            Length(max=200, message='A senha deve ter no mínimo %(max)d caracteres')
        ])

    latitude = StringField(
        'Lat:',
        render_kw={'readonly': True})

    longitude = StringField(
        'Long:',
        render_kw={'readonly': True})     

    categoria = SelectField(
        'Categoria',
        coerce=int,
        validators = [
            DataRequired(message='*Campo Requerido'),
            InputRequired(message=('*Campo Requerido'))
    ])

    subcategoria = SelectField(
        'Subcategoria',
        coerce=int,
        validators = [
            DataRequired(message='*Campo Requerido'),
            InputRequired(message=('*Campo Requerido'))
    ])

    file = FileField(
        'Insira uma foto:',
        validators = [
            InputRequired(message=('*Campo Requerido'))
    ])