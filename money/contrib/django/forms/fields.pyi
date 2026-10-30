from decimal import Decimal
from typing import Any, Sequence

from django import forms
from django.core.validators import _ValidatorCallable
from django.db.models.fields import _ErrorMessagesMapping
from django.utils.choices import _ChoicesCallable, _ChoicesInput
from django.utils.functional import _StrOrPromise

class MoneyField(forms.MultiValueField):
    def __init__(
        self,
        choices: _ChoicesInput | _ChoicesCallable = ...,
        max_value: Decimal | int | float | None = ...,
        min_value: Decimal | int | float | None = ...,
        max_digits: int | None = ...,
        decimal_places: int | None = ...,
        step_size: Decimal | int | float | None = ...,
        required: bool = ...,
        label: _StrOrPromise | None = ...,
        initial: Any | None = ...,
        help_text: _StrOrPromise = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
        show_hidden_initial: bool = ...,
        validators: Sequence[_ValidatorCallable] = ...,
        localize: bool = ...,
        disabled: bool = ...,
        label_suffix: str | None = ...,
    ): ...
