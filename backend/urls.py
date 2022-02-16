from . import api
from backend.views import AddPages, RemoveBookmarks

api.add_resource(AddPages, '/pages/add')
api.add_resource(RemoveBookmarks, '/pages/remove')
