# Generated by Django 4.1 on 2022-08-21 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_runner'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Runner',
        ),
        migrations.RemoveField(
            model_name='person',
            name='name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='shirt_size',
        ),
        migrations.AddField(
            model_name='person',
            name='friends',
            field=models.ManyToManyField(to='app1.person'),
        ),
    ]
