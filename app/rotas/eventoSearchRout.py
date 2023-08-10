from flask import Blueprint

evento_search_bp = Blueprint('eventoSearch', __name__)

from ..controller.eventoSearchController import *