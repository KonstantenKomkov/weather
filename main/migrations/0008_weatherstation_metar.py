# Generated by Django 4.0 on 2022-01-16 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_cloudiness_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherstation',
            name='metar',
            field=models.IntegerField(null=True, verbose_name='metar параметр для запроса'),
        ),
    ]