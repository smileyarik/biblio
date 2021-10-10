# Generated by Django 3.2.8 on 2021-10-10 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('title', models.CharField(max_length=512)),
                ('author', models.CharField(max_length=512)),
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('uniq_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MachineLearningModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=1000)),
                ('version', models.CharField(max_length=128)),
                ('owner', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('path', models.CharField(max_length=256)),
            ],
        ),
    ]