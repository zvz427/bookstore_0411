# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': '收货信息', 'verbose_name': '收货信息'},
        ),
        migrations.AlterModelOptions(
            name='passport',
            options={'verbose_name_plural': '用户信息', 'verbose_name': '用户信息'},
        ),
    ]
