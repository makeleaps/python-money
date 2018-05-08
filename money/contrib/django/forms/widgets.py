from django import forms


class CurrencySelectWidget(forms.MultiWidget):
    """
    Custom widget for entering a value and choosing a currency
    """

    def __init__(self, choices=None, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=choices),
        )
        super(CurrencySelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        try:
            return [value.amount, value.currency]
        except:
            return [None, None]
