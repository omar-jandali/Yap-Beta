# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-08 03:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_localflavor_us.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Checklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='checklist', max_length=100)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('description', models.CharField(default='expense', max_length=200)),
                ('name', models.CharField(default='group name', max_length=100)),
                ('location', models.CharField(default='location', max_length=100)),
                ('status', models.SmallIntegerField(default=1)),
                ('split', models.SmallIntegerField(default=1)),
                ('reference', models.IntegerField(default='101', null=True)),
                ('created_by', models.CharField(default='username', max_length=200, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(default='current user', max_length=22)),
                ('category', models.SmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('friend', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('description', models.CharField(max_length=250, null=True)),
                ('location', models.CharField(max_length=40, null=True)),
                ('count', models.SmallIntegerField(default=1)),
                ('status', models.SmallIntegerField(default=1)),
                ('reference_code', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=100, null=True)),
                ('description', models.CharField(default='some action', max_length=200)),
                ('general', models.SmallIntegerField(default=1)),
                ('validation', models.SmallIntegerField(default=1)),
                ('accepted', models.SmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('checklist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Checklist')),
                ('expense', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Expense')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general.Group')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(default='item', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('checklist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general.Checklist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(default=1)),
                ('funding', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='general.Group')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groups', models.SmallIntegerField(default=1)),
                ('friends', models.SmallIntegerField(default=1)),
                ('expenses', models.SmallIntegerField(default=1)),
                ('searchable', models.SmallIntegerField(default=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='first', max_length=25)),
                ('last_name', models.CharField(default='last', max_length=25)),
                ('bio', models.CharField(default='bio', max_length=220)),
                ('dob', models.DateField(default='1950-01-01')),
                ('street', models.CharField(default='street address', max_length=200)),
                ('city', models.CharField(default='city', max_length=100)),
                ('state', django_localflavor_us.models.USStateField(choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AS', 'American Samoa'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('AA', 'Armed Forces Americas'), ('AE', 'Armed Forces Europe'), ('AP', 'Armed Forces Pacific'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('GU', 'Guam'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('MP', 'Northern Mariana Islands'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VI', 'Virgin Islands'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], default='CA', max_length=2)),
                ('zip_code', models.IntegerField(default=12345)),
                ('phone', models.BigIntegerField(default=0)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('dwolla_id', models.CharField(default='https://api-sandbox.dwolla.com', max_length=200)),
                ('synapse_id', models.CharField(default='123456789', max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(default='current user', max_length=22)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('requested', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SynapseAccounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Bank Account', max_length=100)),
                ('account_id', models.CharField(default='00000', max_length=100)),
                ('account_class', models.CharField(default='Checking', max_length=50)),
                ('bank_name', models.CharField(default='DefaultBank', max_length=150)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('main', models.IntegerField(default=1)),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=150, null=True)),
                ('description', models.CharField(default='some action', max_length=200)),
                ('accepted', models.SmallIntegerField(default=1)),
                ('status', models.SmallIntegerField(default=1)),
                ('reference', models.IntegerField(default='101', null=True)),
                ('validation', models.SmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expense', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Expense')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='expense',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Group'),
        ),
        migrations.AddField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='checklist',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general.Group'),
        ),
        migrations.AddField(
            model_name='checklist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
