from django.urls import re_path, path

from money.tests.views import (
    instance_view,
    model_view,
    model_from_db_view,
    model_form_view,
    regular_form,
    regular_form_edit,
    model_form_edit,
)

urlpatterns = [
    path("instance-view/", instance_view),
    path("model-view/", model_view),
    re_path(
        r"^model-save-view/(?P<amount>\S+)/(?P<currency>\S+)/$", model_from_db_view
    ),
    re_path(r"^model-form-view/(?P<amount>\S+)/(?P<currency>\S+)/$", model_form_view),
    path("regular_form/", regular_form),
    re_path(r"^regular_form/(?P<id>\d+)/$", regular_form_edit),
    re_path(r"^model_form/(?P<id>\d+)/$", model_form_edit),
]
