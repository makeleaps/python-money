from typing import Any

from django import forms
from typing_extensions import TypeAlias
from django.db.models.fields import _FieldChoices

_OptAttrs: TypeAlias = dict[str, Any]

class CurrencySelectWidget(forms.MultiWidget):
    def __init__(
        self,
        choices: _FieldChoices | None = ...,
        attrs: _OptAttrs | None = ...,
    ): ...
