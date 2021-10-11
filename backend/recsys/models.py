from django.db import models
from django.utils import timezone


class MachineLearningModel(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1000)
    version = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    path = models.CharField(max_length=256)


class Book(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    title = models.CharField(max_length=2048)
    author = models.CharField(max_length=2048, null=True)
    uniq_id = models.IntegerField()

    def __str__(self):
        return '{}: "{}", {}'.format(self.id, self.title, self.author)


class User(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    actions = models.ManyToManyField(Book, through='Action')

    def __str__(self):
        return 'User {}'.format(self.id)


class Action(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=128, blank=True)
