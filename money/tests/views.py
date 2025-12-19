from django import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from money.contrib.django.forms.fields import MoneyField
from money.money import Money
from money.tests.models import SimpleMoneyModel


class SampleForm(forms.Form):
    price = MoneyField()


class SampleModelForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = SimpleMoneyModel
        fields = ("name", "price")


def instance_view(request: HttpRequest) -> HttpResponse:
    money = Money("0.0", "JPY")
    return render(request, "view.html", {"money": money})


def model_view(request: HttpRequest) -> HttpResponse:
    instance = SimpleMoneyModel(price=Money("0.0", "JPY"))
    money = instance.price
    return render(request, "view.html", {"money": money})


def model_from_db_view(
    request: HttpRequest, amount: str = "0", currency: str = "XXX"
) -> HttpResponse:
    # db roundtrip
    instance = SimpleMoneyModel.objects.create(price=Money(amount, currency))
    instance = SimpleMoneyModel.objects.get(pk=instance.pk)

    money = instance.price
    return render(request, "view.html", {"money": money})


def model_form_view(
    request: HttpRequest, amount: str = "0", currency: str = "XXX"
) -> HttpResponse:
    cleaned_data = {}
    if request.method == "POST":
        form = SampleModelForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            form.save()
            # Most views would redirect here, but we continue so we can render the data
    else:
        form = SampleModelForm(initial={"price": Money(amount, currency)})

    return render(request, "form.html", {"form": form, "cleaned_data": cleaned_data})


def regular_form(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SampleForm(request.POST)

        if form.is_valid():
            price = form.cleaned_data["price"]
            return render(request, "form.html", {"price": price})
    else:
        form = SampleForm()
    return render(request, "form.html", {"form": form})


def regular_form_edit(request: HttpRequest, id: int) -> HttpResponse:
    instance = get_object_or_404(SimpleMoneyModel, pk=id)
    if request.method == "POST":
        form = SampleForm(request.POST, initial={"price": instance.price})
        form = SampleForm(request.POST, initial={"price": instance.price})

        if form.is_valid():
            price = form.cleaned_data["price"]
            return render(request, "form.html", {"price": price})
    else:
        form = SampleForm(initial={"price": instance.price})
    return render(request, "form.html", {"form": form})


def model_form_edit(request: HttpRequest, id: int) -> HttpResponse:
    instance = get_object_or_404(SimpleMoneyModel, pk=id)
    if request.method == "POST":
        form = SampleModelForm(request.POST, instance=instance)

        if form.is_valid():
            price = form.cleaned_data["price"]
            form.save()
            return render(request, "form.html", {"price": price})
    else:
        form = SampleModelForm(instance=instance)
    return render(request, "form.html", {"form": form})
