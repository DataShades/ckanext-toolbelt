from ckanext.toolbelt.cli import toolbelt

from .db import db
from .search_index import search_index

toolbelt.add_command(search_index)
toolbelt.add_command(db)
