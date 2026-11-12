from typing import Any

from django import forms
from django.utils.choices import _ChoicesInput
from typing_extensions import TypeAlias

_OptAttrs: TypeAlias = dict[str, Any]

class CurrencySelectWidget(forms.MultiWidget):
    def __init__(
        self,
        choices: _ChoicesInput | None = ...,
        attrs: _OptAttrs | None = ...,
    ): ...
