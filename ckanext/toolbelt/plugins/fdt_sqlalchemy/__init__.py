from __future__ import annotations

import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckan import model

try:
    from flask_sqlalchemy import SQLAlchemy, _EngineDebuggingSignalEvents
except ImportError:

    SQLAlchemy = _EngineDebuggingSignalEvents = None

log = logging.getLogger(__name__)


class FdtSqlalchemyPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable)
    p.implements(p.IMiddleware, inherit=True)

    def make_middleware(self, app, config):
        if SQLAlchemy:
            app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
            app.config["SQLALCHEMY_DATABASE_URI"] = config["sqlalchemy.url"]
            SQLAlchemy().init_app(app)
        else:
            version = "3.0" if tk.check_ckan_version("2.11.0") else "2.5"
            log.error(
                "Flask-SQLAlchemy is not installed. "
                "Run `pip install flask-sqlalchemy~=%s` and restart the application",
                version,
            )
        return app

    def configure(self, config):
        if _EngineDebuggingSignalEvents:
            _EngineDebuggingSignalEvents(model.meta.engine, "ckan").register()
