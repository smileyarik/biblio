# Generated by Django 3.2.8 on 2021-10-10 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recsys', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
