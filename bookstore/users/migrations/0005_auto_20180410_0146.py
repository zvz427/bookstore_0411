# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20180410_0038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='recipient_iphone',
            new_name='recipient_phone',
        ),
    ]
