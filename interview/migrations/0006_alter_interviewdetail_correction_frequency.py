# Generated by Django 4.0 on 2021-12-19 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0005_interviewdetail_correction_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewdetail',
            name='correction_frequency',
            field=models.IntegerField(),
        ),
    ]