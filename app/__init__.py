from flask_login import LoginManager
from flask import Blueprint, Flask, render_template

app = Flask(__name__)

public = Blueprint('public', __name__)
@public.route('/')
def home():
        return render_template('index.html')

login_manager = LoginManager(app)
login_manager.login_view = "login.login"
login_manager.login_message = u"Por favor, realize o login para acessar a página"

from .rotas.loginRout import login_bp
from .rotas.eventoRout import evento_bp
from .rotas.eventoSearchRout import evento_search_bp

app.register_blueprint(public)
app.register_blueprint(login_bp)
app.register_blueprint(evento_bp)
app.register_blueprint(evento_search_bp)



