# Generated by Django 2.2.1 on 2020-10-14 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('call_tracking', '0004_auto_20201014_1617'),
    ]

    operations = [
        migrations.RenameField(
            model_name='call',
            old_name='proxy_number',
            new_name='forwarding_number',
        ),
    ]