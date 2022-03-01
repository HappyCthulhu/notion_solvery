from flask import Blueprint
from flask_restful import Api
from .views import AddPages

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


api.add_resource(AddPages, 'pages/add')

