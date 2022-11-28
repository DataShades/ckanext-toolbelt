from __future__ import annotations
from typing import Optional

from typing_extensions import TypedDict, TypeAlias

from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy.orm import Query

import ckan.model as model_

Model: TypeAlias = "model_"
AlchemySession = ScopedSession


class SelectOption(TypedDict):
    text: Optional[str]
    value: str
