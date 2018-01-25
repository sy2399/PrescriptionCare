# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-25 03:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_num', models.CharField(max_length=20)),
                ('customer', models.CharField(max_length=256)),
                ('assigned_group', models.CharField(max_length=256)),
                ('assigned_group_position', models.CharField(max_length=256)),
                ('contract_start_date', models.DateField(blank=True, null=True)),
                ('contract_end_date', models.DateField(blank=True, null=True)),
                ('note', models.CharField(max_length=256)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]