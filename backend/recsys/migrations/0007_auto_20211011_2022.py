# Generated by Django 3.2.8 on 2021-10-11 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recsys', '0006_auto_20211010_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=2048),
        ),
    ]