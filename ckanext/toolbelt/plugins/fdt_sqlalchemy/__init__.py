from __future__ import annotations

import ckan.plugins as p

from ckan import model

try:
    from flask_sqlalchemy import SQLAlchemy, _EngineDebuggingSignalEvents
except ImportError:

    SQLAlchemy = _EngineDebuggingSignalEvents = None


class FdtSqlalchemyPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable)
    p.implements(p.IMiddleware, inherit=True)

    def make_middleware(self, app, config):
        if SQLAlchemy:
            app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
            app.config["SQLALCHEMY_DATABASE_URI"] = config["sqlalchemy.url"]
            SQLAlchemy().init_app(app)
        return app


    def configure(self, config):
        if _EngineDebuggingSignalEvents:
            _EngineDebuggingSignalEvents(model.meta.engine, "ckan").register()
