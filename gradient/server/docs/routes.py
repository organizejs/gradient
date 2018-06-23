from flask import Blueprint, render_template

bp = Blueprint('docs', __name__, url_prefix='/docs')


@bp.route('/home')
def home():
    '''
    Render the home page of the docs
    '''
    return render_template('/docs/index.html')


