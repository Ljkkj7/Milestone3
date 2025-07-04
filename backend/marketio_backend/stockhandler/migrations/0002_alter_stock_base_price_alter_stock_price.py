# Generated by Django 5.2.3 on 2025-06-18 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockhandler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='base_price',
            field=models.DecimalField(decimal_places=2, default=100.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stock',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
