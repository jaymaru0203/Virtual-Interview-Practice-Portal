# Generated by Django 3.2 on 2021-12-12 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0011_auto_20211203_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='interviewwdetails',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]