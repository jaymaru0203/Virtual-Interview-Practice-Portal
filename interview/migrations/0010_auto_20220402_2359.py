# Generated by Django 3.1.7 on 2022-04-02 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0009_alter_question_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='interviewdetail',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]