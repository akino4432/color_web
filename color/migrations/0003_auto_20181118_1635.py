# Generated by Django 2.1.3 on 2018-11-18 07:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('color', '0002_auto_20181118_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='color',
            name='note',
            field=models.TextField(blank=True, verbose_name='ノート'),
        ),
        migrations.AlterField(
            model_name='color',
            name='lang',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='color.Lang', verbose_name='言語'),
        ),
    ]
