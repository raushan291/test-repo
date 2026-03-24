from flask import Blueprint

payments_bp = Blueprint('payments', __name__, url_prefix='/payments', template_folder='templates', static_folder='static')

from . import routes # noqa: E402, F401