# Generated by Django 5.1.1 on 2024-09-14 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='player1',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='match',
            name='player2',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='match',
            name='winner',
            field=models.CharField(max_length=100),
        ),
    ]