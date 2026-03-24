from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')

from . import routes # noqa: E402, F401