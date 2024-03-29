# Generated by Django 2.2.1 on 2019-06-10 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_group_no', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SkillLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_level_name', models.CharField(max_length=100)),
            ],
        ),
    ]
