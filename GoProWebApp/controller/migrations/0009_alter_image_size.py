# Generated by Django 5.0.4 on 2024-07-04 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0008_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='size',
            field=models.FloatField(null=True),
        ),
    ]