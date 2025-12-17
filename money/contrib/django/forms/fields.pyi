from decimal import Decimal
from typing import Any, Sequence

from django import forms
from django.utils.functional import _StrOrPromise
from django.db.models.fields import _ErrorMessagesT, _ChoicesCallable, _FieldChoices
from django.core.validators import _ValidatorCallable

class MoneyField(forms.MultiValueField):
    def __init__(
        self,
        choices: _FieldChoices | _ChoicesCallable = ...,
        max_value: Decimal | int | float | None = ...,
        min_value: Decimal | int | float | None = ...,
        max_digits: int | None = ...,
        decimal_places: int | None = ...,
        step_size: Decimal | int | float | None = ...,
        required: bool = ...,
        label: _StrOrPromise | None = ...,
        initial: Any | None = ...,
        help_text: _StrOrPromise = ...,
        error_messages: _ErrorMessagesT | None = ...,
        show_hidden_initial: bool = ...,
        validators: Sequence[_ValidatorCallable] = ...,
        localize: bool = ...,
        disabled: bool = ...,
        label_suffix: str | None = ...,
    ): ...
