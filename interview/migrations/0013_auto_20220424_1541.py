# Generated by Django 3.2.9 on 2022-04-24 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0012_auto_20220424_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='avg_confidence',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interview',
            name='avg_mistakes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]