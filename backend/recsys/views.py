import pickle
import random
import numpy as np

from distutils.util import strtobool

from django.http import HttpResponse
from django.template import loader

from rest_framework import views, viewsets
from rest_framework.response import Response

from recsys.models import Book, User, Action, Recommendation
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
            user_id = 0
            user = User.objects.get(id=user_id)

        history_books = [(action.time, action.book_id) for action in Action.objects.filter(user__id=user_id)]
        history_books.sort(reverse=True)
        history_books_ids = [bid for _, bid in history_books]
        history_books = Book.objects.filter(id__in=history_books_ids)
        history_books = [{"id": book.book_id, "title": book.title, "author": book.author} for book in history_books]

        rec_books = [(rec.book_id, rec.score) for rec in Recommendation.objects.filter(user__id=user_id)]
        rec_books.sort(key=lambda x: x[1], reverse=True)
        rec_books_ids = [i for i, _ in rec_books]
        rec_books_scores = {i: score for i, score in rec_books}
        rec_books_ids = rec_books_ids[:5]

        rec_books = Book.objects.filter(id__in=rec_books_ids)
        rec_books = [{
            "id": book.book_id,
            "title": book.title,
            "author": book.author,
            "scf_id": book.id,
            "score": rec_books_scores[book.id]
        } for book in rec_books]
        rec_books.sort(key=lambda x: x["score"], reverse=True)

        response = {
            "recommendations": rec_books,
            "history": history_books
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
