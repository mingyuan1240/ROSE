from django.conf.urls import url

from common.http.methods import *
from common.dispatch import method_dispatch
from main import views

urlpatterns = [
    url(r'^v0/patient$', views.CreatePatientView.as_view()),
    url(r'^v0/upload/file/token', views.GetQiniuTokenView.as_view()),
    url(r'^v0/patient/(\d+)$', method_dispatch(
        GET = views.PatientDetailView.as_view(),
        DELETE = views.DeletePatientView.as_view(),
        PUT = views.UpdatePatientView.as_view()
    ))
]
