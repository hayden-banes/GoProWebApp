# Generated by Django 5.0.4 on 2024-05-09 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0005_alter_gopro_keep_alive_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='timelapse',
            name='task_signal',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='timelapse',
            name='task_id',
            field=models.IntegerField(default=-1),
        ),
    ]
