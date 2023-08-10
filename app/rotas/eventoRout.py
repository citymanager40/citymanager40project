from flask import Blueprint

evento_bp = Blueprint('evento', __name__)

from ..controller.eventoController import *