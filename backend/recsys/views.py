import random

from distutils.util import strtobool

from django.http import HttpResponse
from django.template import loader

from rest_framework import views, viewsets
from rest_framework.response import Response

from recsys.models import Book, User, Action
from recsys.serializers import BookSerializer, UserSerializer, ActionSerializer


class LightFMModel:
    def __init__(self, path):
        with open(path, 'rb') as r:
            self.model = pickle.load(r)

    def predict(self, user_id, k):
        user_idx = self.model.user_id2idx[user_id]
        items_indices = np.arange(len(self.model.item_idx2id))
        scores = collab_model.predict(user_idx, items_indices)
        return [self.model.item_idx2id[i] for i in np.argsort(-scores)[:k]]


class ModelsRegistry:
    models = dict()
    model_types = {
        "lightfm": LightFMModel
    }

    @classmethod
    def get_model(cls, name):
        if name in cls.models:
            return cls.models.get(name)


class RecPredictView(views.APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id", None)
        if user_id is None:
            return Response({})

        user_id = int(user_id)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({})

        books_ids = [action.id for action in user.actions.all()]
        books = Book.objects.filter(id__in=books_ids)
        books = [{"id": book.id, "title": book.title, "author": book.author} for book in books]
        response = {
            "recommendations": [],
            "history": books
        }

        if strtobool(request.GET.get("view", "false")):
            template = loader.get_template('recsys/predict.html')
            return HttpResponse(template.render(response))
        return Response(response)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActionViewSet(viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
