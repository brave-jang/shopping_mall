# Generated by Django 3.2 on 2021-04-30 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0002_rename_user_to_coupon_use_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='active',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]
