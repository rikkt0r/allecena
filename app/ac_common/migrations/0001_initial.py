# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import ac_common.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.CharField(unique=True, max_length=80)),
                ('auth_token', models.CharField(max_length=128, blank=True)),
                ('auth_expiry_date', models.DateTimeField(null=True, blank=True)),
                ('allegro_user_id', models.CharField(max_length=60, blank=True)),
                ('allegro_user_name', models.CharField(max_length=60, blank=True)),
                ('ebay_user_id', models.CharField(max_length=60, blank=True)),
                ('ebay_user_name', models.CharField(max_length=60, blank=True)),
                ('first_name', models.CharField(max_length=40, blank=True)),
                ('last_name', models.CharField(max_length=40, blank=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', ac_common.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('parent_id', models.IntegerField(blank=True)),
                ('parent_name', models.TextField(blank=True)),
            ],
        ),
    ]
