# Generated by Django 5.0.1 on 2024-02-03 01:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0010_alter_bankrupt_is_bankrupt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='is_bankrupt',
        ),
    ]