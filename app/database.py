from app import app
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/citymanager'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)

@app.errorhandler(Exception)
def internal_error(e):
    db.session.rollback()
    return render_template('erro.html', e=e)