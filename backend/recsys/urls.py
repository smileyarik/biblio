from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from recsys.views import RecPredictView

router = DefaultRouter()

urlpatterns = [
    url("", include(router.urls)),
    url(r"api/predict$", RecPredictView.as_view(), name="predict"),
]
