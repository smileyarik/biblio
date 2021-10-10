from rest_framework import serializers

from recsys.models import Book, Action, User


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "uniq_id")


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ("book_id", "user_id")


class UserSerializer(serializers.ModelSerializer):
    actions = serializers.SlugRelatedField(read_only=True, many=True, slug_field='title')
    class Meta:
        model = User
        fields = ("id", "actions")
