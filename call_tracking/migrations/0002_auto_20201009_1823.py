# Generated by Django 2.2.1 on 2020-10-09 18:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('call_tracking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('direction_is_incoming', models.BooleanField(default=True)),
                ('start_timestamp', models.DateTimeField(auto_now_add=True)),
                ('end_timestamp', models.DateTimeField(auto_now=True)),
                ('source_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('forwarding_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('channel', models.CharField(choices=[('Bandit', 'Bandit Sign'), ('Web', 'Online'), ('Mail', 'Direct Mail')], default='Bandit', max_length=50, verbose_name='Marketing Channel')),
            ],
        ),
        migrations.CreateModel(
            name='LeadSources',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='It helps to be specific for easy attribution. E.g. "Bandit sign @ i20 exit 31"', max_length=100)),
                ('incoming_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='A phone number purchased through Twilio', max_length=128, null=True, region=None)),
                ('forwarding_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='People who call this lead source will be connected with this phone number. Must include international prefix - e.g. +1 555 555 5555', max_length=128, region=None)),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PurchasedNumbers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UsersPhoneNumbers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='lead',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lead',
            name='zipcode',
            field=models.CharField(default='No zipcode', max_length=10),
        ),
        migrations.AlterField(
            model_name='lead',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='call_tracking.LeadSources'),
        ),
        migrations.DeleteModel(
            name='LeadSource',
        ),
        migrations.AddField(
            model_name='campaign',
            name='lead_sources',
            field=models.ManyToManyField(to='call_tracking.LeadSources'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='call',
            name='lead_source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='call_tracking.LeadSources'),
        ),
        migrations.AddField(
            model_name='call',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
