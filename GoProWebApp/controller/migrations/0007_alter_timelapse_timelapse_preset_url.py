# Generated by Django 5.0.4 on 2024-05-09 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0006_timelapse_task_signal_alter_timelapse_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelapse',
            name='timelapse_preset_url',
            field=models.CharField(default='/gopro/camera/presets/load?id=65536', editable=False, max_length=40),
        ),
    ]
