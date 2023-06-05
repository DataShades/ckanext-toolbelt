from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from werkzeug.utils import import_string

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model

if TYPE_CHECKING:
    from ckan.common import CKANConfig
    from ckan.config.middleware.flask_app import CKANFlask


SQLAlchemy = import_string("flask_sqlalchemy:SQLAlchemy", True)

_EngineDebuggingSignalEvents = import_string(
    "flask_sqlalchemy:_EngineDebuggingSignalEvents",
    True,
)
record_queries = import_string("flask_sqlalchemy.record_queries", True)


log = logging.getLogger(__name__)


class FdtSqlalchemyPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable)
    p.implements(p.IMiddleware, inherit=True)

    def make_middleware(self, app: CKANFlask, config: CKANConfig):
        if not SQLAlchemy:
            version = "3.0" if tk.check_ckan_version("2.11.0") else "2.5"
            log.error(
                "Flask-SQLAlchemy is not installed. "
                "Run `pip install flask-sqlalchemy~=%s` and restart the application",
                version,
            )
            return app

        app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
        app.config["SQLALCHEMY_DATABASE_URI"] = config["sqlalchemy.url"]
        SQLAlchemy().init_app(app)

        return app

    def configure(self, _config: CKANConfig):
        # v2.5
        if _EngineDebuggingSignalEvents:
            _EngineDebuggingSignalEvents(model.meta.engine, "ckan").register()

        # v3.0 / select and explain are not compatible with flask-debugtoolbar
        if record_queries:
            record_queries._listen(model.meta.engine)
