from django.conf.urls import url

from common.http.methods import *
from common.dispatch import method_dispatch
from main import views

urlpatterns = [
    url(r'^v0/patient$', views.CreatePatientView.as_view()),
]
