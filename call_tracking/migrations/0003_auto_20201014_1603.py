# Generated by Django 2.2.1 on 2020-10-14 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_tracking', '0002_auto_20201009_1823'),
    ]

    operations = [
        migrations.RenameField(
            model_name='call',
            old_name='direction_is_incoming',
            new_name='inbound',
        ),
        migrations.AddField(
            model_name='call',
            name='in_browser',
            field=models.BooleanField(default=False),
        ),
    ]
