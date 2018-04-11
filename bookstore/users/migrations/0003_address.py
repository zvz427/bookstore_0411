# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180403_0911'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('is_del', models.BooleanField(default=False, verbose_name='删除标记')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('recipient_name', models.CharField(max_length=20, verbose_name='收件人')),
                ('recipient_addr', models.CharField(max_length=256, verbose_name='收件地址')),
                ('zip_code', models.CharField(max_length=6, verbose_name='邮政编码')),
                ('recipient_iphone', models.CharField(max_length=11, verbose_name='联系电话')),
                ('is_default', models.BooleanField(default=False, verbose_name='是否默认地址')),
                ('passport', models.ForeignKey(to='users.Passport', verbose_name='账户')),
            ],
            options={
                'db_table': 's_user_address',
            },
        ),
    ]
