# Generated by Django 3.1.6 on 2021-02-07 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queryprocessor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionmodel',
            name='variable_types',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]