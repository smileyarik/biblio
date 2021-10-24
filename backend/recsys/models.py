from django.db import models
from django.utils import timezone


class Book(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    title = models.CharField(max_length=2048)
    author = models.CharField(max_length=2048, null=True)
    book_id = models.IntegerField()

    def __str__(self):
        return '{} ({}): "{}", {}'.format(self.id, self.book_id, self.title, self.author)


class User(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    actions = models.ManyToManyField(Book, through='Action', related_name='actions')
    recommendations = models.ManyToManyField(Book, through='Recommendation', related_name='recommendations')

    def __str__(self):
        return 'User {}'.format(self.id)


class Action(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=128, blank=True)


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    score = models.FloatField()
