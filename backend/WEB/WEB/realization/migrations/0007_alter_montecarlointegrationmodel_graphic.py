# Generated by Django 5.1.2 on 2024-11-03 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realization', '0006_alter_montecarlointegrationmodel_graphic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='montecarlointegrationmodel',
            name='graphic',
            field=models.ImageField(blank=True, null=True, upload_to='media/solved'),
        ),
    ]
