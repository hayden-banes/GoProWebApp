# Generated by Django 5.0.4 on 2024-05-08 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0002_gopro_keep_alive_signal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gopro',
            name='keep_alive_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]