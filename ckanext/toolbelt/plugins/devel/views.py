from __future__ import annotations

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.logic import parse_params

bp = Blueprint("toolbelt_devel", __name__)


class EvalView(MethodView):
    def get(self) -> str:
        return tk.render("toolbelt_devel/eval.html")

    def post(self):
        data_dict = parse_params(tk.request.form)
        try:
            return tk.get_action("toolbelt_devel_eval")({}, data_dict)
        except tk.NotAuthorized:
            return tk.abort(403)


bp.add_url_rule("/ckan-admin/devel/eval", view_func=EvalView.as_view("eval"))
