# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-07-18 10:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpressInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logistic_code', models.CharField(max_length=400, verbose_name='快递单号')),
                ('shipper_code', models.CharField(max_length=10, verbose_name='物流公司编码')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='express', to='orders.OrderInfo', verbose_name='订单编号')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='express', to=settings.AUTH_USER_MODEL, verbose_name='业务员')),
            ],
            options={
                'verbose_name': '物流信息',
                'verbose_name_plural': '物流信息',
                'db_table': 'tb_express_info',
            },
        ),
    ]
