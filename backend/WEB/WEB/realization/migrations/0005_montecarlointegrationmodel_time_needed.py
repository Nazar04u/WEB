# Generated by Django 5.1.2 on 2024-11-03 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realization', '0004_montecarlointegrationmodel_delete_photomodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='montecarlointegrationmodel',
            name='time_needed',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
