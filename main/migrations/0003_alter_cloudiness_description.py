# Generated by Django 3.2.2 on 2021-07-15 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_cloudiness_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cloudiness',
            name='description',
            field=models.CharField(max_length=200, unique=True, verbose_name='общая облачность'),
        ),
    ]
