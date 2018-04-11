# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20180410_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordergoods',
            name='comment',
            field=models.CharField(verbose_name='商品评论', null=True, blank=True, max_length=128),
        ),
    ]
