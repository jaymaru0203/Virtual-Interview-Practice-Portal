# Generated by Django 3.2.9 on 2021-12-03 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0007_auto_20211202_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]