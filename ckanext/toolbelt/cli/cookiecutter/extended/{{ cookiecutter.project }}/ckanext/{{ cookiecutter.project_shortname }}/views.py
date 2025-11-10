"""Views of the {{ cookiecutter.project_shortname }} plugin.

All blueprints added to `__all__` are registered as blueprints inside Flask
app. If you have multiple blueprints, create them inside submodules of
`ckanext.{{ cookiecutter.project_shortname }}.views` and re-export via `__all__`.

Example:
    ```python
    from .custom import custom_bp
    from .data import data_bp

    __all__ = ["custom_bp", "data_bp"]
    ```
"""

from __future__ import annotations

import io
import csv
from typing import Any, cast

from flask import Blueprint, make_response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.logic import parse_params

__all__ = ["bp"]

bp = Blueprint("{{ cookiecutter.project_shortname }}", __name__)


# instead of catching exceptions inside every view, it's usually more
# convenient to register handlers for the exception class.
@bp.errorhandler(tk.ObjectNotFound)
def not_found_handler(error: tk.ObjectNotFound) -> tuple[str, int]:
    """Generic handler for ObjectNotFound exception."""
    return (
        tk.render(
            "error_document_template.html",
            {
                "code": 404,
                "content": f"Object not found: {error.message}",
                "name": "Not found",
            },
        ),
        404,
    )


# error handler renders standard error page. If you want to render
# view-specific page with a flash message instead, it's better it try/catch
# inside the view.
@bp.errorhandler(tk.NotAuthorized)
def not_authorized_handler(error: tk.NotAuthorized) -> tuple[str, int]:
    """Generic handler for NotAuthorized exception."""
    return (
        tk.render(
            "error_document_template.html",
            {
                "code": 403,
                "content": error.message or "Not authorized to view this page",
                "name": "Not authorized",
            },
        ),
        403,
    )


# use `Blueprint.route` decorators to register function-based views. This
# approach is more readable than using `Blueprint.add_url_rule`.
@bp.route("/{{ cookiecutter.project_shortname }}/page")
def page():
    """Basic page."""
    return "Hello, {{ cookiecutter.project_shortname }}!"


@bp.route("/{{ cookiecutter.project_shortname }}/page-redirect")
def page_redirect():
    """Complex page."""
    return tk.redirect_to("{{ cookiecutter.project_shortname }}.page")


# Class-based views cannot be registered via decorator
class ComplexView(MethodView):
    """Complex view.

    Pellentesque dapibus suscipit ligula.  Donec posuere augue in quam.  Etiam
    vel tortor sodales tellus ultricies commodo.  Suspendisse potenti.  Aenean
    in sem ac leo mollis blandit.  Donec neque quam, dignissim in, mollis nec,
    sagittis eu, wisi.  Phasellus lacus.  Etiam laoreet quam sed arcu.
    Phasellus at dui in ligula mollis ultricies.  Integer placerat tristique
    nisl.  Praesent augue.  Fusce commodo.  Vestibulum convallis, lorem a
    tempus semper, dui dui euismod elit, vitae placerat urna tortor vitae
    lacus.  Nullam libero mauris, consequat quis, varius et, dictum id, arcu.
    Mauris mollis tincidunt felis.  Aliquam feugiat tellus ut neque.  Nulla
    facilisis, risus a rhoncus fermentum, tellus tellus lacinia purus, et
    dictum nunc justo sit amet elit.

    Attributes:
        template: page template of the view.
    """

    template = "{{ cookiecutter.project_shortname }}/complex.html"

    def _prepare(self, word: str) -> dict[str, Any]:
        tk.check_access(
            "{{ cookiecutter.project_shortname }}_get_sum",
            {},
            {
                "left": word,
                "right": word,
            },
        )

        username = tk.current_user.name
        if tk.current_user.is_authenticated:
            user = cast(model.User, tk.current_user)
        else:
            user = None

        return {
            "word": word,
            "username": username,
            "user": user,
        }

    def get(self, word: str):
        data = self._prepare(word)
        return tk.render(self.template, data)

    def post(self, word: str):
        data = self._prepare(word)

        params = parse_params(tk.request.form)

        try:
            result = tk.get_action("{{ cookiecutter.project_shortname }}_get_sum")(
                {},
                params,
            )
        except tk.ValidationError as err:
            data["errors"] = err.error_dict
            for field, msg in err.error_summary.items():
                tk.h.flash_error(f"{field}: {msg}")

            return tk.render(self.template, data)

        tk.h.flash_success("Yay! {}".format(result["sum"]))
        return tk.redirect_to("{{ cookiecutter.project_shortname }}.page")


@bp.route("/stats/tracking_data", methods=["GET"])
def export_tracking_data():
    """Exports tracking data as a CSV file.

    Query params:
        start (optional) - filter records from this date (inclusive)
        end (optional) - filter records up to this date (inclusive)
    """
    start_date = tk.request.args.get("start")
    end_date = tk.request.args.get("end")

    query = """
        SELECT
            url,
            tracking_type,
            COUNT(*) AS total_count,
            MIN(access_timestamp) AS first_access,
            MAX(access_timestamp) AS last_access
        FROM tracking_raw
        WHERE url IS NOT NULL AND url <> ''
    """

    # Add date filter if provided
    params = {}
    if start_date:
        query += " AND access_timestamp >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND access_timestamp <= :end_date"
        params["end_date"] = end_date

    query += " GROUP BY url, tracking_type ORDER BY total_count DESC;"

    results = model.Session.execute(query, params)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["url", "tracking_type", "count", "first_access", "last_access"])

    for row in results:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=page_views.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


# we don't have to specify `methods` parameter, because `MethodView` already
# contains this information
bp.add_url_rule(
    "/{{ cookiecutter.project_shortname }}/complex/<word>",
    view_func=ComplexView.as_view("complex"),
)
