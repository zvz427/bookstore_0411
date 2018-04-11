# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordergoods',
            options={'verbose_name_plural': '订单商品信息', 'verbose_name': '订单商品信息'},
        ),
        migrations.AlterModelOptions(
            name='orderinfo',
            options={'verbose_name_plural': '订单信息', 'verbose_name': '订单信息'},
        ),
    ]
