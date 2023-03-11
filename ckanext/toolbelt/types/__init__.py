from __future__ import annotations

from typing import Optional

from sqlalchemy.orm.scoping import ScopedSession
from typing_extensions import TypeAlias, TypedDict

import ckan.model as model_

Model: TypeAlias = "model_"
AlchemySession = ScopedSession


class SelectOption(TypedDict):
    text: Optional[str]
    value: str
