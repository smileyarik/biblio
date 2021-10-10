from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from recsys.views import RecPredictView, BookViewSet, UserViewSet, ActionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'users', UserViewSet)
router.register(r'actions', ActionViewSet)

urlpatterns = [
    url("", include(router.urls)),
    url(r"predict$", RecPredictView.as_view(), name="predict"),
]
