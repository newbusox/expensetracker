# Generated by Django 2.1.5 on 2019-05-26 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0051_employee_daily_pay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='daily_pay',
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
    ]