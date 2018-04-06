from flask import Blueprint

bp = Blueprint('docs', __name__, url_prefix='/docs')


@bp.route('/home')
def home():
    '''
    Render the home page of the docs
    '''
    return render_template('documentation.html')


@bp.route('/home')
def home():
    '''
    Render the home page of the docs
    '''
    return render_template('documentation.html')

