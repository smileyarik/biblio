# Generated by Django 3.2.8 on 2021-10-10 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recsys', '0003_alter_book_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('type', models.CharField(max_length=128)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recsys.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recsys.user')),
            ],
        ),
    ]
