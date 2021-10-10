import random

from rest_framework import views, viewsets
from rest_framework.response import Response

from recsys.models import Book, User, Action
from recsys.serializers import BookSerializer, UserSerializer, ActionSerializer


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
