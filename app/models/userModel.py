from app import login_manager
from ..database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    __tablename__ = 'tb_usuario_usu'
    __table_args__ = {"schema":"comum"}
    
    id = db.Column('id_usuario_usu', db.Integer, autoincrement=True, primary_key=True)
    email = db.Column('txt_email_usu', db.String(200), nullable=False, unique=True)
    cpf = db.Column('txt_cpf_usu', db.String(11), nullable=False, unique=True)

    def __init__(self, name, email, cpf, password):
        self.email = email
        self.cpf = cpf
        self.password = generate_password_hash(password)

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)