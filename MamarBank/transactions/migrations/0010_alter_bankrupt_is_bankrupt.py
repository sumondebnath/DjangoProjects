# Generated by Django 5.0.1 on 2024-02-01 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0009_rename_bankrupt_transaction_is_bankrupt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankrupt',
            name='is_bankrupt',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
