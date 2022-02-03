from .. import toolbelt
from .search_index import search_index
from .db import db
toolbelt.add_command(search_index)
toolbelt.add_command(db)
